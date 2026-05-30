/**
 * Landing / Login Page (/)
 * Shows the Google Sign-In button.
 * After successful login, redirects to /dashboard.
 */

"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useGoogleLogin } from "@react-oauth/google";
import toast from "react-hot-toast";
import { useAuth } from "@/lib/auth-context";
import api from "@/lib/api";

export default function LoginPage() {
  const { user, login, isLoading } = useAuth();
  const router = useRouter();

  // If already logged in, skip to dashboard
  useEffect(() => {
    if (!isLoading && user) router.replace("/dashboard");
  }, [user, isLoading, router]);

  /**
   * useGoogleLogin from @react-oauth/google uses the "implicit" flow:
   * the user clicks the button → Google popup → we receive an access_token.
   * We then exchange it for an ID token by calling Google's userinfo endpoint,
   * BUT the simpler approach used here is to use the "authorization_code" flow
   * with @react-oauth/google's GoogleLogin component (see below).
   *
   * We use the GoogleLogin component which gives us the credential (ID token)
   * directly via its onSuccess callback.
   */

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600" />
      </div>
    );
  }

  return (
    <main className="min-h-screen bg-gradient-to-br from-primary-50 to-indigo-100 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-xl p-10 w-full max-w-md text-center">
        {/* Logo / Title */}
        <div className="mb-8">
          <div className="w-16 h-16 bg-primary-600 rounded-2xl flex items-center justify-center mx-auto mb-4">
            <span className="text-white text-2xl">✓</span>
          </div>
          <h1 className="text-3xl font-bold text-gray-900">Task Manager</h1>
          <p className="text-gray-500 mt-2">
            Collaborate, assign, and track tasks with your team
          </p>
        </div>

        {/* Feature highlights */}
        <ul className="text-left space-y-2 mb-8 text-sm text-gray-600">
          {[
            "Create and assign tasks to teammates",
            "Set priorities and due dates",
            "Get email notifications via Gmail",
            "Track task status in real-time",
          ].map((f) => (
            <li key={f} className="flex items-center gap-2">
              <span className="text-green-500 font-bold">✓</span> {f}
            </li>
          ))}
        </ul>

        {/* Google Sign-In button (rendered via @react-oauth/google) */}
        <GoogleSignInButton onLogin={login} />

        <p className="text-xs text-gray-400 mt-6">
          By signing in, you agree to our Terms of Service.
        </p>
      </div>
    </main>
  );
}

// ── Isolated component so we can use useGoogleLogin hook ────────────────────
function GoogleSignInButton({ onLogin }: { onLogin: (token: string) => Promise<void> }) {
  const router = useRouter();

  /**
   * @react-oauth/google's useGoogleLogin with flow="auth-code" is the
   * recommended approach for sending the auth code to a backend.
   * Here we use the simpler credential_response approach via GoogleLogin component.
   * We import GoogleLogin dynamically to avoid SSR issues.
   */
  const { GoogleLogin } = require("@react-oauth/google");

  return (
    <div className="flex justify-center">
      <GoogleLogin
        onSuccess={async (credentialResponse: { credential?: string }) => {
          if (!credentialResponse.credential) {
            toast.error("Google sign-in failed: no credential received");
            return;
          }
          try {
            await onLogin(credentialResponse.credential);
            toast.success("Welcome! Redirecting to dashboard...");
            router.push("/dashboard");
          } catch {
            toast.error("Login failed. Please try again.");
          }
        }}
        onError={() => toast.error("Google sign-in failed")}
        useOneTap
        shape="rectangular"
        size="large"
        text="signin_with_google"
        theme="outline"
      />
    </div>
  );
}
