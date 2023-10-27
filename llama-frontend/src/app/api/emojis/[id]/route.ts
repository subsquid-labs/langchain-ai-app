import { prisma } from "@/server/db";
import { EmojiContextProps, Response } from "@/server/utils";
import { NextResponse } from "next/server";

export const runtime = "edge";
export const fetchCache = "force-no-store";
export const revalidate = 0;

export async function GET(request: Request, { params }: EmojiContextProps) {
  try {
    const emoji = null;
    if (!emoji) return Response.emojiNotFound();

    return NextResponse.json({ emoji }, { status: 200 });
  } catch (error) {
    console.error(error);
    return Response.internalServerError();
  }
}
