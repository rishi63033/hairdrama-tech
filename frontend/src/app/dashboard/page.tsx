/**
 * Dashboard Page (/dashboard)
 * Shows a summary of tasks and the main task list.
 * Protected — redirects to / if not authenticated.
 */

"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import toast from "react-hot-toast";
import { useAuth } from "@/lib/auth-context";
import api from "@/lib/api";
import { Task } from "@/types";
import Navbar from "@/components/Navbar";
import TaskCard from "@/components/TaskCard";
import CreateTaskModal from "@/components/CreateTaskModal";
import StatsBar from "@/components/StatsBar";

export default function DashboardPage() {
  const { user, isLoading } = useAuth();
  const router = useRouter();

  const [tasks, setTasks] = useState<Task[]>([]);
  const [fetching, setFetching] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [filter, setFilter] = useState<"all" | "mine" | "assigned">("all");

  // Auth guard
  useEffect(() => {
    if (!isLoading && !user) router.replace("/");
  }, [user, isLoading, router]);

  // Fetch tasks on mount
  useEffect(() => {
    if (user) fetchTasks();
  }, [user]);

  async function fetchTasks() {
    setFetching(true);
    try {
      const res = await api.get<Task[]>("/api/tasks");
      setTasks(res.data);
    } catch {
      toast.error("Failed to load tasks");
    } finally {
      setFetching(false);
    }
  }

  async function handleComplete(taskId: string) {
    try {
      await api.patch(`/api/tasks/${taskId}/complete`);
      toast.success("Task marked as completed! Creator has been notified.");
      fetchTasks();
    } catch {
      toast.error("Failed to complete task");
    }
  }

  async function handleDelete(taskId: string) {
    try {
      await api.delete(`/api/tasks/${taskId}`);
      toast.success("Task deleted");
      fetchTasks();
    } catch {
      toast.error("Failed to delete task");
    }
  }

  // Apply filter
  const filteredTasks = tasks.filter((t) => {
    if (filter === "mine") return t.creator.id === user?.id;
    if (filter === "assigned") return t.assignee?.id === user?.id;
    return true;
  });

  if (isLoading || !user) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />

      <main className="max-w-6xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-8">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">
              Welcome back, {user.name.split(" ")[0]}! 👋
            </h1>
            <p className="text-gray-500 mt-1">Here's what's on your plate</p>
          </div>
          <button
            onClick={() => setShowCreateModal(true)}
            className="bg-primary-600 text-white px-5 py-2.5 rounded-lg font-medium hover:bg-primary-700 transition-colors flex items-center gap-2"
          >
            <span className="text-lg">+</span> New Task
          </button>
        </div>

        {/* Stats summary */}
        <StatsBar tasks={tasks} />

        {/* Filter tabs */}
        <div className="flex gap-2 mb-6 mt-8">
          {(["all", "mine", "assigned"] as const).map((f) => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors capitalize ${
                filter === f
                  ? "bg-primary-600 text-white"
                  : "bg-white text-gray-600 border border-gray-200 hover:bg-gray-50"
              }`}
            >
              {f === "all" ? "All Tasks" : f === "mine" ? "Created by Me" : "Assigned to Me"}
            </button>
          ))}
        </div>

        {/* Task list */}
        {fetching ? (
          <div className="flex justify-center py-16">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600" />
          </div>
        ) : filteredTasks.length === 0 ? (
          <div className="text-center py-16 text-gray-400">
            <p className="text-5xl mb-4">📭</p>
            <p className="text-lg font-medium">No tasks yet</p>
            <p className="text-sm">Create your first task to get started</p>
          </div>
        ) : (
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {filteredTasks.map((task) => (
              <TaskCard
                key={task.id}
                task={task}
                currentUserId={user.id}
                onComplete={handleComplete}
                onDelete={handleDelete}
                onRefresh={fetchTasks}
              />
            ))}
          </div>
        )}
      </main>

      {/* Create Task Modal */}
      {showCreateModal && (
        <CreateTaskModal
          onClose={() => setShowCreateModal(false)}
          onCreated={() => {
            setShowCreateModal(false);
            fetchTasks();
          }}
        />
      )}
    </div>
  );
}
