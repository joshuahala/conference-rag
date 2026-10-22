import { createClient } from "jsr:@supabase/supabase-js@2";
import { corsHeaders } from "./cors.ts";

/**
 * Verify the caller's JWT inside the function.
 *
 * We deploy with --no-verify-jwt because the API gateway's built-in check
 * can reject valid modern (ES256) session tokens. supabase.auth.getUser()
 * talks to Auth and handles those tokens correctly.
 *
 * Returns { user } on success, or { error: Response } (401) on failure.
 */
export async function requireAuth(
  req: Request,
): Promise<{ user: { id: string; email?: string } } | { error: Response }> {
  const authHeader = req.headers.get("Authorization");
  if (!authHeader) {
    return {
      error: new Response(
        JSON.stringify({ error: "Missing Authorization header" }),
        {
          status: 401,
          headers: { ...corsHeaders, "Content-Type": "application/json" },
        },
      ),
    };
  }

  const supabase = createClient(
    Deno.env.get("SUPABASE_URL") ?? "",
    Deno.env.get("SUPABASE_ANON_KEY") ?? "",
    { global: { headers: { Authorization: authHeader } } },
  );

  const { data: { user }, error } = await supabase.auth.getUser();

  if (error || !user) {
    return {
      error: new Response(
        JSON.stringify({ error: "Invalid or expired token" }),
        {
          status: 401,
          headers: { ...corsHeaders, "Content-Type": "application/json" },
        },
      ),
    };
  }

  return { user };
}
