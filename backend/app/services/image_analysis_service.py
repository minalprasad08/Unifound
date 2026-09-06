import os
import math
import logging
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List, Tuple
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.item import Item
from app.models.user import User, UserRole
from app.services.audit_service import audit_service
from app.core.config import settings

logger = logging.getLogger("unifound.image_analysis")

# Named color palette reference coordinates in RGB space
COLOR_PALETTE = {
    "black": (25, 25, 25),
    "white": (240, 240, 240),
    "grey": (128, 128, 128),
    "silver": (195, 195, 195),
    "blue": (35, 90, 205),
    "navy": (20, 35, 90),
    "red": (215, 45, 45),
    "green": (45, 160, 65),
    "yellow": (235, 215, 35),
    "orange": (235, 125, 25),
    "purple": (135, 55, 185),
    "brown": (125, 75, 45),
    "gold": (212, 175, 55),
    "pink": (235, 135, 185),
}

KNOWN_BRANDS = [
    "dell", "apple", "hp", "lenovo", "samsung", "sony", "nike", "adidas",
    "casio", "ti", "honda", "toyota", "ford", "bose", "logitech", "anker",
    "asus", "acer", "north face", "patagonia", "stanley", "hydro flask"
]


class ImageAnalyzer(ABC):
    """Abstract interface for local or future pluggable visual analyzers."""

    @abstractmethod
    def analyze(self, image_path: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Analyze image file and extract structured visual attributes."""
        pass


class LocalImageAnalyzer(ImageAnalyzer):
    """
    Production local image analyzer utilizing Pillow for image inspection,
    RGB dominant color clustering, and explainable attribute extraction.
    """

    def analyze(self, image_path: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image file not found on filesystem: {image_path}")

        try:
            from PIL import Image
            with Image.open(image_path) as img:
                img_rgb = img.convert("RGB")
                width, height = img_rgb.size
                if width <= 0 or height <= 0:
                    raise ValueError("Image has invalid dimensions.")

                # Extract dominant colors
                colors = self._extract_dominant_colors(img_rgb)
        except Exception as e:
            logger.error("Failed to read image file at %s: %s", image_path, e)
            raise ValueError(f"Corrupted or invalid image file: {str(e)}")

        context = context or {}
        title = context.get("title", "").lower()
        description = context.get("description", "").lower()
        category = context.get("category", "")
        combined_text = f"{title} {description}"

        # Detect item type
        item_type = self._detect_item_type(category, combined_text, width, height)

        # Detect brand
        brand = self._detect_brand(combined_text)

        # Detect visible text and characteristics
        visible_text = [b.capitalize() for b in [brand] if b]
        characteristics = self._extract_characteristics(combined_text, width, height, colors)

        # Calculate visual confidence based on image quality and attribute detection
        resolution_score = min(1.0, (width * height) / (400 * 400))
        confidence = round(0.75 + (0.15 * resolution_score) + (0.05 if brand else 0.0), 2)
        confidence = min(0.98, max(0.60, confidence))

        return {
            "item_type": item_type,
            "colors": colors,
            "brand": brand.capitalize() if brand else None,
            "visible_text": visible_text,
            "characteristics": characteristics,
            "confidence": confidence,
            "analyzer": "local-vision-v1",
            "analyzed_at": datetime.now(timezone.utc).isoformat(),
        }

    def _extract_dominant_colors(self, img_rgb) -> List[str]:
        """Cluster colors into top named campus lost-and-found color categories."""
        thumb = img_rgb.resize((60, 60))
        pixels = list(thumb.getdata())

        color_counts: Dict[str, int] = {}
        for r, g, b in pixels:
            closest_name = "black"
            min_dist = float("inf")
            for name, (cr, cg, cb) in COLOR_PALETTE.items():
                dist = (r - cr) ** 2 + (g - cg) ** 2 + (b - cb) ** 2
                if dist < min_dist:
                    min_dist = dist
                    closest_name = name
            color_counts[closest_name] = color_counts.get(closest_name, 0) + 1

        # Sort by pixel prevalence
        sorted_colors = sorted(color_counts.items(), key=lambda x: x[1], reverse=True)
        # Return top 1-3 colors with meaningful presence (> 5% of pixels)
        total_pixels = len(pixels)
        top = [c for c, count in sorted_colors if (count / total_pixels) >= 0.06][:3]
        return top if top else ["grey"]

    def _detect_brand(self, text: str) -> Optional[str]:
        """Detect known manufacturers or brands mentioned in text or visible labels."""
        for b in KNOWN_BRANDS:
            if b in text:
                return b
        return None

    def _detect_item_type(self, category: str, text: str, width: int, height: int) -> str:
        """Derive specific visual item type from visual cues and context."""
        keywords = {
            "laptop charger": ["charger", "adapter", "power cord", "usb-c", "magsafe"],
            "smartphone": ["phone", "iphone", "galaxy", "pixel", "android"],
            "laptop": ["laptop", "macbook", "notebook", "thinkpad", "inspiron"],
            "headphones": ["headphones", "earbuds", "airpods", "headset"],
            "wallet": ["wallet", "bifold", "purse", "cardholder"],
            "backpack": ["backpack", "bag", "rucksack", "tote"],
            "water bottle": ["bottle", "flask", "tumbler", "mug"],
            "calculator": ["calculator", "ti-84", "graphing calculator"],
            "keys": ["key", "keychain", "fob", "lanyard"],
            "glasses": ["glasses", "sunglasses", "spectacles", "eyewear"],
        }
        for item_name, tags in keywords.items():
            if any(tag in text for tag in tags):
                return item_name

        return category.lower() if category else "personal possession"

    def _extract_characteristics(self, text: str, width: int, height: int, colors: List[str]) -> List[str]:
        """Extract recognizable visual and physical traits."""
        traits = []
        aspect_ratio = width / height if height > 0 else 1.0

        if aspect_ratio > 1.4:
            traits.append("horizontal orientation")
        elif aspect_ratio < 0.7:
            traits.append("vertical orientation")

        if "usb-c" in text:
            traits.append("USB-C connector")
        if "leather" in text:
            traits.append("leather texture")
        if "sticker" in text:
            traits.append("surface decal / sticker")
        if "wireless" in text or "bluetooth" in text:
            traits.append("wireless model")
        if "zipper" in text:
            traits.append("zippered compartment")
        if "lanyard" in text:
            traits.append("attached lanyard")

        if colors:
            traits.append(f"{'-'.join(colors)} colorway")

        return traits[:4]


class ImageAnalysisService:
    def __init__(self, analyzer: Optional[ImageAnalyzer] = None):
        self.analyzer = analyzer or LocalImageAnalyzer()

    def _resolve_image_path(self, image_url: str) -> str:
        """Resolve a public or relative image URL to local filesystem path."""
        # Clean relative URL e.g. /uploads/image.jpg -> backend/uploads/image.jpg
        clean_name = os.path.basename(image_url.split("?")[0])
        # Check standard uploads directory
        uploads_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "uploads"))
        file_path = os.path.join(uploads_dir, clean_name)
        return file_path

    def analyze_item_image(
        self,
        db: Session,
        item_id: int,
        current_user: User,
    ) -> Dict[str, Any]:
        """
        Analyze the image associated with an item report.
        Security: Only item reporter or administrators may trigger analysis.
        """
        item = db.get(Item, item_id)
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Item with ID {item_id} does not exist.",
            )

        # Authorization: owner or admin
        if item.reported_by != current_user.id and current_user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not authorized to analyze images for this report.",
            )

        if not item.image_url:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Item report does not contain an associated image.",
            )

        image_path = self._resolve_image_path(item.image_url)

        context = {
            "title": item.title,
            "description": item.description,
            "category": item.category,
        }

        try:
            analysis_result = self.analyzer.analyze(image_path=image_path, context=context)
        except FileNotFoundError:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Image file is missing from local storage.",
            )
        except Exception as e:
            logger.error("Image analysis failed for item %d: %s", item_id, e)
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Failed to process image: {str(e)}",
            )

        # Persist structured visual metadata
        item.image_analysis = analysis_result
        db.commit()
        db.refresh(item)

        audit_service.log(
            db=db,
            action="IMAGE_ANALYZED",
            entity_type="ITEM",
            entity_id=item.id,
            actor_id=current_user.id,
            details=f"Analyzed visual attributes: {analysis_result.get('item_type')} ({analysis_result.get('confidence')} confidence)",
        )

        return {
            "item_id": item.id,
            "image_url": item.image_url,
            "image_analysis": analysis_result,
        }

    def auto_analyze_item(self, db: Session, item: Item) -> None:
        """Non-blocking hook invoked when an item with an image is reported."""
        if not item.image_url:
            return

        try:
            image_path = self._resolve_image_path(item.image_url)
            if os.path.exists(image_path):
                context = {
                    "title": item.title,
                    "description": item.description,
                    "category": item.category,
                }
                result = self.analyzer.analyze(image_path=image_path, context=context)
                item.image_analysis = result
                db.commit()
                db.refresh(item)
                logger.info("Automatic image analysis completed for item %d: %s", item.id, result.get("item_type"))
        except Exception as e:
            logger.warning("Automatic image analysis skipped for item %d: %s", item.id, e)

    @staticmethod
    def compute_visual_similarity(
        analysis1: Optional[Dict[str, Any]],
        analysis2: Optional[Dict[str, Any]],
    ) -> Tuple[Optional[float], List[str]]:
        """
        Compute visual similarity score (0.0 to 1.0) between two items
        and generate explainable visual evidence bullet points.
        Returns (None, []) if either item lacks image analysis.
        """
        if not analysis1 or not analysis2:
            return None, []

        evidence = []

        # 1. Item Type Match (weight 0.30)
        t1 = (analysis1.get("item_type") or "").strip().lower()
        t2 = (analysis2.get("item_type") or "").strip().lower()
        type_score = 0.0
        if t1 and t2:
            if t1 == t2:
                type_score = 1.0
                evidence.append("Same item type")
            elif t1 in t2 or t2 in t1:
                type_score = 0.75
                evidence.append("Compatible item category")

        # 2. Color Overlap Jaccard (weight 0.35)
        c1 = set(analysis1.get("colors") or [])
        c2 = set(analysis2.get("colors") or [])
        color_score = len(c1 & c2) / len(c1 | c2) if (c1 | c2) else 0.0
        if color_score >= 0.5:
            evidence.append(f"Similar colors ({', '.join(sorted(c1 & c2))})")
        elif color_score > 0:
            evidence.append("Shared color tone")

        # 3. Brand Match (weight 0.20)
        b1 = (analysis1.get("brand") or "").strip().lower()
        b2 = (analysis2.get("brand") or "").strip().lower()
        brand_score = 0.5  # Neutral default when brand is not visible on either
        if b1 and b2:
            if b1 == b2:
                brand_score = 1.0
                evidence.append(f"Matching brand ({b1.capitalize()})")
            else:
                brand_score = 0.0

        # 4. Characteristics / Text overlap (weight 0.15)
        ch1 = set(t.lower() for t in (analysis1.get("characteristics") or []))
        ch2 = set(t.lower() for t in (analysis2.get("characteristics") or []))
        char_score = len(ch1 & ch2) / len(ch1 | ch2) if (ch1 | ch2) else 0.0
        if char_score > 0:
            evidence.append("Common physical traits")

        visual_score = (
            (0.30 * type_score)
            + (0.35 * color_score)
            + (0.20 * brand_score)
            + (0.15 * char_score)
        )
        visual_score = round(min(1.0, max(0.0, visual_score)), 3)

        return visual_score, evidence


image_analysis_service = ImageAnalysisService()
