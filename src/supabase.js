import { createClient } from "@supabase/supabase-js";

export const supabase = createClient(
  "https://awzxxzaspmwqgrywplnu.supabase.co",
  "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImF3enh4emFzcG13cWdyeXdwbG51Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzY5MjI0NjgsImV4cCI6MjA5MjQ5ODQ2OH0._1uvuSwKvWCKUxilJuC-AiO9U2-rKz6yB6-MPrzwYxg"
);