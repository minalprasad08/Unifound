export type UserRole = 'USER' | 'ADMIN';

export interface User {
  id: number;
  email: string;
  full_name: string;
  role: UserRole;
  phone?: string | null;
  department?: string | null;
  student_id?: string | null;
  avatar_url?: string | null;
  is_active: boolean;
  is_verified: boolean;
  created_at: string;
  updated_at: string;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData {
  email: string;
  password: string;
  full_name: string;
  phone?: string;
  department?: string;
  student_id?: string;
  role?: UserRole;
}

export interface AuthResponse {
  user: User;
  access_token: string;
  token_type: string;
}

export interface ProfileUpdateData {
  full_name?: string;
  phone?: string;
  department?: string;
  student_id?: string;
  avatar_url?: string;
}

export interface HealthStatus {
  status: string;
  service: string;
  version: string;
  environment: string;
  database: string;
  timestamp: string;
}

// Item Types for Phase 4
export type ItemType = 'LOST' | 'FOUND';
export type ItemStatus = 'OPEN' | 'CLAIM_PENDING' | 'CLAIMED' | 'RESOLVED' | 'CLOSED';

export interface ItemReporter {
  id: number;
  full_name: string;
  email: string;
  phone?: string | null;
  department?: string | null;
}

export interface ImageAnalysis {
  item_type?: string | null;
  colors: string[];
  brand?: string | null;
  visible_text: string[];
  characteristics: string[];
  confidence: number;
  analyzer: string;
  analyzed_at: string;
}

export interface Item {
  id: number;
  item_type: ItemType;
  title: string;
  description: string;
  category: string;
  location: string;
  incident_date: string;
  image_url?: string | null;
  image_analysis?: ImageAnalysis | null;
  status: ItemStatus;
  reported_by: number;
  created_at: string;
  updated_at: string;
  reporter?: ItemReporter;
}

export interface ItemReportInput {
  title: string;
  description: string;
  category: string;
  location: string;
  incident_date: string;
  image_url?: string | null;
}

export interface ItemUpdateInput {
  title?: string;
  description?: string;
  category?: string;
  location?: string;
  incident_date?: string;
  image_url?: string | null;
  status?: ItemStatus;
}

export interface ItemSearchParams {
  q?: string;
  item_type?: ItemType;
  category?: string;
  location?: string;
  status?: ItemStatus;
  from_date?: string;
  to_date?: string;
  sort_by?: 'created_at' | 'incident_date';
  sort_order?: 'asc' | 'desc';
  page?: number;
  page_size?: number;
}

export interface ItemSearchResponse {
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
  items: Item[];
}

export type ClaimStatus = 'PENDING' | 'APPROVED' | 'REJECTED' | 'CANCELLED';

export interface Claim {
  id: number;
  item_id: number;
  claimant_id: number;
  description: string;
  evidence?: string | null;
  status: ClaimStatus;
  admin_notes?: string | null;
  reviewed_by?: number | null;
  reviewed_at?: string | null;
  created_at: string;
  updated_at: string;
  item?: Item;
  claimant?: User;
}

export interface ClaimSubmitInput {
  item_id: number;
  description: string;
  evidence?: string;
}

export interface ClaimReviewInput {
  admin_notes?: string;
}

export interface AdminClaimsResponse {
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
  claims: Claim[];
}

export type NotificationType = 'INFO' | 'CLAIM_UPDATE' | 'MATCH_ALERT' | 'SYSTEM';

export interface Notification {
  id: number;
  user_id: number;
  title: string;
  message: string;
  type: NotificationType;
  is_read: boolean;
  created_at: string;
}

export interface RecentActivityItem {
  id: number;
  action: string;
  entity_type: string;
  entity_id?: number | null;
  actor_id?: number | null;
  details?: string | null;
  created_at: string;
}

export interface AdminStats {
  total_users: number;
  total_items: number;
  items_by_type: { [key: string]: number };
  items_by_status: { [key: string]: number };
  pending_claims: number;
  total_claims: number;
  recent_activity: RecentActivityItem[];
}

export interface ItemMatchCandidate {
  item: Item;
  confidence: number;
  title_score: number;
  description_score: number;
  category_score: number;
  location_score: number;
  date_score: number;
  visual_score?: number | null;
  visual_evidence?: string[];
  explanation: string;
}

export interface ItemMatchesResponse {
  source_item_id: number;
  source_item_title: string;
  source_item_type: string;
  total: number;
  page: number;
  page_size: number;
  matches: ItemMatchCandidate[];
}
export interface AnalyticsDateBucket {
  date: string;
  count: number;
}

export interface CategoryCount {
  category: string;
  count: number;
}

export interface LocationCount {
  location: string;
  count: number;
}

export interface AdminAnalytics {
  total_users: number;
  active_users: number;
  total_lost_reports: number;
  total_found_reports: number;
  open_reports: number;
  resolved_reports: number;
  closed_reports: number;
  pending_claims: number;
  approved_claims: number;
  rejected_claims: number;
  match_count: number;
  high_confidence_matches: number;
  notifications_generated: number;
  reports_by_category: CategoryCount[];
  reports_by_location: LocationCount[];
  lost_vs_found_distribution: { lost: number; found: number };
  claims_over_time: AnalyticsDateBucket[];
  reports_over_time: AnalyticsDateBucket[];
  recent_activity: RecentActivityItem[];
  period: string;
  from_date?: string | null;
  to_date?: string | null;
}

