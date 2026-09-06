import re
import math
import difflib
import logging
from datetime import datetime
from typing import List, Tuple, Dict, Any, Optional
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select
from app.models.item import Item, ItemType, ItemStatus

logger = logging.getLogger("unifound.matching")

# English stop words for lightweight text normalization
STOP_WORDS = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and",
    "any", "are", "as", "at", "be", "because", "been", "before", "being", "below",
    "between", "both", "but", "by", "could", "did", "do", "does", "doing", "down",
    "during", "each", "few", "for", "from", "further", "had", "has", "have",
    "having", "he", "her", "here", "hers", "herself", "him", "himself", "his",
    "how", "i", "if", "in", "into", "is", "it", "its", "itself", "just", "me",
    "more", "most", "my", "myself", "no", "nor", "not", "of", "off", "on", "once",
    "only", "or", "other", "ought", "our", "ours", "ourselves", "out", "over", "own",
    "same", "she", "should", "so", "some", "such", "than", "that", "the", "their",
    "theirs", "them", "themselves", "then", "there", "these", "they", "this",
    "those", "through", "to", "too", "under", "until", "up", "very", "was", "we",
    "were", "what", "when", "where", "which", "while", "who", "whom", "why", "with",
    "would", "you", "your", "yours", "yourself", "yourselves"
}


class MatchingWeights:
    """Configurable weights for multi-factor similarity scoring."""
    def __init__(
        self,
        description: float = 0.35,
        title: float = 0.25,
        category: float = 0.15,
        location: float = 0.15,
        date: float = 0.10,
    ):
        total = description + title + category + location + date
        assert total > 0, "Total weights must be greater than zero."
        self.description = description / total
        self.title = title / total
        self.category = category / total
        self.location = location / total
        self.date = date / total


DEFAULT_WEIGHTS = MatchingWeights()


class MatchingService:
    def __init__(self, weights: Optional[MatchingWeights] = None):
        self.weights = weights or DEFAULT_WEIGHTS

    @staticmethod
    def tokenize(text: str) -> List[str]:
        """Extract alphanumeric tokens in lowercase, ignoring punctuation."""
        if not text:
            return []
        cleaned = re.sub(r"[^a-zA-Z0-9\s]", " ", text.lower())
        tokens = [t for t in cleaned.split() if t and t not in STOP_WORDS]
        return tokens

    @staticmethod
    def get_trigrams(text: str) -> set:
        """Extract character 3-grams for typo-tolerant lexical matching."""
        clean = re.sub(r"\s+", " ", text.lower().strip())
        if len(clean) < 3:
            return {clean} if clean else set()
        return {clean[i : i + 3] for i in range(len(clean) - 2)}

    def compute_title_similarity(self, title1: str, title2: str) -> float:
        """
        Compute explainable title similarity combining word Jaccard, character trigrams,
        and sequence matching ratio.
        """
        t1 = title1.strip().lower()
        t2 = title2.strip().lower()
        if not t1 or not t2:
            return 0.0
        if t1 == t2:
            return 1.0

        # 1. Word token Jaccard
        w1 = set(self.tokenize(t1))
        w2 = set(self.tokenize(t2))
        word_jaccard = len(w1 & w2) / len(w1 | w2) if (w1 | w2) else 0.0

        # 2. Character trigrams Jaccard (handles typos & spelling variations)
        tri1 = self.get_trigrams(t1)
        tri2 = self.get_trigrams(t2)
        tri_jaccard = len(tri1 & tri2) / len(tri1 | tri2) if (tri1 | tri2) else 0.0

        # 3. Sequence matcher ratio
        seq_ratio = difflib.SequenceMatcher(None, t1, t2).ratio()

        score = (0.45 * word_jaccard) + (0.30 * tri_jaccard) + (0.25 * seq_ratio)
        return min(1.0, max(0.0, score))

    def compute_description_similarity(self, desc1: str, desc2: str) -> float:
        """
        Compute description similarity using sublinear TF cosine similarity
        and significant token overlap.
        """
        d1 = desc1.strip().lower()
        d2 = desc2.strip().lower()
        if not d1 or not d2:
            return 0.0
        if d1 == d2:
            return 1.0

        tokens1 = self.tokenize(d1)
        tokens2 = self.tokenize(d2)
        if not tokens1 or not tokens2:
            return difflib.SequenceMatcher(None, d1, d2).ratio()

        # Compute Term Frequencies with sublinear scaling
        tf1: Dict[str, float] = {}
        for t in tokens1:
            tf1[t] = 1.0 + math.log(tf1.get(t, 0) + 1.0)

        tf2: Dict[str, float] = {}
        for t in tokens2:
            tf2[t] = 1.0 + math.log(tf2.get(t, 0) + 1.0)

        # Cosine similarity
        all_words = set(tf1.keys()) | set(tf2.keys())
        dot_product = sum(tf1.get(w, 0.0) * tf2.get(w, 0.0) for w in all_words)
        norm1 = math.sqrt(sum(v * v for v in tf1.values()))
        norm2 = math.sqrt(sum(v * v for v in tf2.values()))
        cosine_sim = dot_product / (norm1 * norm2) if (norm1 > 0 and norm2 > 0) else 0.0

        # Token overlap ratio relative to the shorter description
        overlap_ratio = len(set(tokens1) & set(tokens2)) / min(len(set(tokens1)), len(set(tokens2)))

        score = (0.65 * cosine_sim) + (0.35 * overlap_ratio)
        return min(1.0, max(0.0, score))

    @staticmethod
    def compute_category_similarity(cat1: str, cat2: str) -> float:
        """Check category equality or categorical compatibility."""
        c1 = cat1.strip().lower()
        c2 = cat2.strip().lower()
        if not c1 or not c2:
            return 0.0
        if c1 == c2:
            return 1.0
        if c1 in c2 or c2 in c1:
            return 0.75
        return 0.0

    def compute_location_similarity(self, loc1: str, loc2: str) -> float:
        """Evaluate spatial similarity through normalized token overlap and sequence ratio."""
        l1 = loc1.strip().lower()
        l2 = loc2.strip().lower()
        if not l1 or not l2:
            return 0.0
        if l1 == l2:
            return 1.0

        toks1 = set(self.tokenize(l1))
        toks2 = set(self.tokenize(l2))
        token_overlap = len(toks1 & toks2) / len(toks1 | toks2) if (toks1 | toks2) else 0.0
        seq_ratio = difflib.SequenceMatcher(None, l1, l2).ratio()

        score = (0.60 * token_overlap) + (0.40 * seq_ratio)
        return min(1.0, max(0.0, score))

    @staticmethod
    def compute_date_proximity(dt1: datetime, dt2: datetime) -> float:
        """
        Calculate date proximity using smooth exponential decay.
        Identical date -> 1.0.
        3 days apart -> ~0.88.
        7 days apart -> ~0.75.
        14 days apart -> ~0.57.
        30 days apart -> ~0.30.
        """
        diff_seconds = abs((dt1 - dt2).total_seconds())
        diff_days = diff_seconds / 86400.0
        decay = math.exp(-0.04 * diff_days)
        return min(1.0, max(0.0, decay))

    def generate_explanation(
        self,
        confidence: float,
        title_score: float,
        desc_score: float,
        cat_score: float,
        loc_score: float,
        date_score: float,
    ) -> str:
        """Synthesize explainable rationale from individual feature contributions."""
        reasons = []

        if cat_score >= 0.75:
            reasons.append("matching category")
        if title_score >= 0.75:
            reasons.append("high title similarity")
        elif title_score >= 0.50:
            reasons.append("moderate title overlap")

        if desc_score >= 0.75:
            reasons.append("strong description correlation")
        elif desc_score >= 0.50:
            reasons.append("similar descriptive details")

        if loc_score >= 0.70:
            reasons.append("consistent campus location")
        elif loc_score >= 0.40:
            reasons.append("nearby location")

        if date_score >= 0.80:
            reasons.append("close incident timeframe")

        if not reasons:
            return "Low match confidence: disparate descriptions and reporting dates."

        if confidence >= 80.0:
            return "Very strong match: " + ", ".join(reasons) + "."
        elif confidence >= 60.0:
            return "Strong match: " + ", ".join(reasons) + "."
        elif confidence >= 40.0:
            return "Possible match based on " + ", ".join(reasons) + "."
        else:
            return "Weak correlation with " + ", ".join(reasons) + "."

    def score_candidate(self, source: Item, candidate: Item) -> Dict[str, Any]:
        """Compute all individual feature scores and the composite confidence score."""
        title_score = round(self.compute_title_similarity(source.title, candidate.title), 3)
        desc_score = round(self.compute_description_similarity(source.description, candidate.description), 3)
        cat_score = round(self.compute_category_similarity(source.category, candidate.category), 3)
        loc_score = round(self.compute_location_similarity(source.location, candidate.location), 3)
        date_score = round(self.compute_date_proximity(source.incident_date, candidate.incident_date), 3)

        raw_confidence = (
            (self.weights.description * desc_score)
            + (self.weights.title * title_score)
            + (self.weights.category * cat_score)
            + (self.weights.location * loc_score)
            + (self.weights.date * date_score)
        ) * 100.0

        confidence = round(min(100.0, max(0.0, raw_confidence)), 1)
        explanation = self.generate_explanation(
            confidence=confidence,
            title_score=title_score,
            desc_score=desc_score,
            cat_score=cat_score,
            loc_score=loc_score,
            date_score=date_score,
        )

        # Check if visual analysis is available for both items
        from app.services.image_analysis_service import image_analysis_service
        visual_score, visual_evidence = image_analysis_service.compute_visual_similarity(
            source.image_analysis,
            candidate.image_analysis,
        )

        if visual_score is not None:
            # 90% text/date matching + 10% visual similarity
            combined_raw = (0.90 * raw_confidence) + (0.10 * (visual_score * 100.0))
            confidence = round(min(100.0, max(0.0, combined_raw)), 1)
            if visual_evidence:
                explanation += f" Visual evidence: {', '.join(visual_evidence)}."

        return {
            "confidence": confidence,
            "title_score": title_score,
            "description_score": desc_score,
            "category_score": cat_score,
            "location_score": loc_score,
            "date_score": date_score,
            "visual_score": visual_score,
            "visual_evidence": visual_evidence,
            "explanation": explanation,
        }

    def find_matches(
        self,
        db: Session,
        source_item: Item,
        min_confidence: float = 0.0,
        page: int = 1,
        page_size: int = 10,
    ) -> Tuple[int, List[Dict[str, Any]]]:
        """
        Rank potential candidates for source_item.
        Strict Rules:
          - Only compare LOST <-> FOUND.
          - Never compare LOST <-> LOST or FOUND <-> FOUND.
          - Exclude same item.
          - Exclude CLOSED or RESOLVED items.
          - Filter by min_confidence.
          - Sort by confidence descending.
        """
        # Determine target opposite item type
        target_type = ItemType.FOUND if source_item.item_type == ItemType.LOST else ItemType.LOST

        # Query candidates of opposite type that are not closed or resolved
        stmt = (
            select(Item)
            .options(joinedload(Item.reporter))
            .where(
                Item.item_type == target_type,
                Item.id != source_item.id,
                Item.status.in_([ItemStatus.OPEN, ItemStatus.CLAIM_PENDING]),
            )
        )
        candidates = list(db.execute(stmt).scalars().all())

        results = []
        for cand in candidates:
            score_data = self.score_candidate(source_item, cand)
            if score_data["confidence"] >= min_confidence:
                results.append({
                    "item": cand,
                    **score_data,
                })

        # Rank candidates by confidence descending
        results.sort(key=lambda x: x["confidence"], reverse=True)

        total = len(results)
        offset = (page - 1) * page_size
        paginated = results[offset : offset + page_size]

        return total, paginated

    def on_item_created(self, db: Session, item: Item) -> None:
        """
        Automatic match hook executed upon item creation.
        Non-blocking: Finds potential candidates and notifies reporters when confidence >= 70%.
        """
        try:
            total, top_matches = self.find_matches(
                db=db,
                source_item=item,
                min_confidence=40.0,
                page=1,
                page_size=5,
            )
            if total > 0:
                top_match = top_matches[0]
                conf = top_match["confidence"]
                cand_item = top_match["item"]

                logger.info(
                    "Automatic match detection: Found %d potential candidate(s) for newly reported %s item '%s' (ID %d). Top confidence: %.1f%%",
                    total,
                    item.item_type.value,
                    item.title,
                    item.id,
                    conf,
                )

                # If confidence >= 70%, trigger event notifications for both reporters
                if conf >= 70.0:
                    from app.services.notification_service import notification_service
                    
                    # Notify new item reporter
                    if item.reported_by:
                        notification_service.notify_match_alert(
                            db=db,
                            user_id=item.reported_by,
                            source_title=item.title,
                            matched_title=cand_item.title,
                            matched_location=cand_item.location,
                            confidence=conf,
                            item_id=item.id,
                            match_item_id=cand_item.id,
                        )

                    # Notify opposite item reporter
                    if cand_item.reported_by and cand_item.reported_by != item.reported_by:
                        notification_service.notify_match_alert(
                            db=db,
                            user_id=cand_item.reported_by,
                            source_title=cand_item.title,
                            matched_title=item.title,
                            matched_location=item.location,
                            confidence=conf,
                            item_id=cand_item.id,
                            match_item_id=item.id,
                        )
        except Exception as e:
            logger.warning("Automatic match detection encountered an error for item %d: %s", item.id, e)



matching_service = MatchingService()
