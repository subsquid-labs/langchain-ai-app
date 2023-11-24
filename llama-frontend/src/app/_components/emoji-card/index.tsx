import { formatPrompt } from "@/lib/utils";
import { getEmoji } from "@/server/get-emoji";
import { ButtonCard } from "./button-card";

interface EmojiCardProps {
  id: string;
  alwaysShowDownloadBtn?: boolean;
}

export async function EmojiCard({ id, alwaysShowDownloadBtn }: EmojiCardProps) {
  const data = null;

  return <div />;
}
