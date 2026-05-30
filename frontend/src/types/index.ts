// ─── Shared TypeScript types used across the frontend ──────────────────────

export interface User {
  id: string;
  name: string;
  email: string;
  avatar_url?: string;
}

export type TaskStatus = "pending" | "in_progress" | "completed";
export type TaskPriority = "low" | "medium" | "high";

export interface Task {
  id: string;
  title: string;
  description?: string;
  status: TaskStatus;
  priority: TaskPriority;
  due_date?: string;         // ISO date string "YYYY-MM-DD"
  created_at: string;
  updated_at: string;
  completed_at?: string;
  creator: User;
  assignee?: User | null;
}

export interface CreateTaskPayload {
  title: string;
  description?: string;
  priority?: TaskPriority;
  due_date?: string;
  assignee_id?: string;
}

export interface UpdateTaskPayload extends Partial<CreateTaskPayload> {
  status?: TaskStatus;
}

export interface AuthContextType {
  user: User | null;
  token: string | null;
  login: (idToken: string) => Promise<void>;
  logout: () => void;
  isLoading: boolean;
}
