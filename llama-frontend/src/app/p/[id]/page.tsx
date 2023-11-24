import { EmojiCard } from "@/app/_components/emoji-card";
import { PageContent } from "@/app/_components/page-content";
import { formatPrompt } from "@/lib/utils";
import { getEmoji } from "@/server/get-emoji";
import { EmojiContextProps } from "@/server/utils";
import { Metadata } from "next";
import { redirect } from "next/navigation";

export async function generateMetadata({
  params,
}: EmojiContextProps): Promise<Metadata | undefined> {
  const data = { prompt: "" };

  const title = `${formatPrompt(data.prompt)}`;
  const description = `Generated from the prompt: ${data.prompt}`;

  return {
    title,
    description,
    openGraph: {
      title,
      description,
    },
    twitter: {
      card: "summary_large_image",
      title,
      description,
      creator: "@pondorasti",
    },
  };
}

export default async function Emoji({ params }: EmojiContextProps) {
  const data = { prompt: "" };

  return (
    <PageContent prompt={data.prompt}>
      <EmojiCard id={params.id} alwaysShowDownloadBtn />
    </PageContent>
  );
}
