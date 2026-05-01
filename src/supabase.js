import { createClient } from "@supabase/supabase-js";

export const supabase = createClient(
  "https://awzxxzaspmwqgrywplnu.supabase.co",
  "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImF3enh4emFzcG13cWdyeXdwbG51Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3MTM5NjQ3MDEsImV4cCI6MjAyOTU0MDcwMX0.Ql3IBVB7HuV1MBkG2Ys5yX0ZMoMlXJCB4MBiELyFTng"
);