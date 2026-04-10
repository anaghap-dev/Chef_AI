import { createClient } from "@supabase/supabase-js";

const supabaseUrl = "https://mwvvqrqryipqaqayvpnr.supabase.co";
const supabaseKey = "sb_publishable_7zvg4VektrW_ZxXWhFbOhA_abEE5FwI";

export const supabase = createClient(supabaseUrl, supabaseKey);