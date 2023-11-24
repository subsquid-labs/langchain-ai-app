"use client";
import { CornerDownLeft } from "lucide-react";
import { experimental_useFormStatus as useFormStatus } from "react-dom";
import { Loader } from "../loader";
import { use, useCallback, useEffect, useRef, useState } from "react";
import { createEmoji } from "./action";
// @ts-expect-error
import { experimental_useFormState as useFormState } from "react-dom";
import toast from "react-hot-toast";
import React from "react";
import { set } from "zod";
import Typewriter from "typewriter-effect";

interface ButtonProps {
  sum: (a: number, b: number) => number;
  showText: () => void;
  getAnswer: () => Promise<any>;

  // 👇️ turn off type checking
  doSomething: (params: any) => any;
}

interface EmojiFormProps {
  initialPrompt?: string;
}
async function getAnswer(prompt: string) {
  const res = await fetch(
    "https://flask-production-1ca5.up.railway.app/post_json",
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        prompt: prompt,
      }),
    }
  );
  console.log("RESPONSE");
  console.log(res);
  if (!res.ok) {
    return "Error, try a different prompt.";
  }

  const json = await res.json();
  console.log("JSON");
  console.log(json);
  return json["text"];
}

export function EmojiForm({ initialPrompt }: EmojiFormProps) {
  const [texting, setTexting] = React.useState("");
  let [renderCount, setRenderCount] = React.useState(0);
  const [prompt, setPrompt] = React.useState("");
  const [rendered, setRendered] = React.useState(false);
  const [formState, formAction] = useFormState(createEmoji);
  const submitRef = useRef<React.ElementRef<"button">>(null);
  const [token, setToken] = useState("");
  // const [typer, setTyper] = useState(<></>);
  useEffect(() => {
    if (!formState) return;
    toast.error(formState.message);
  }, [formState]);

  //let { pending } = useFormStatus();
  let [pending, setPending] = useState(false);

  function updateTexting(newTexting: string) {
    setTexting(newTexting);
  }

  return (
    <>
      <form
        action={formAction}
        className="bg-black rounded-xl shadow-lg h-fit flex flex-row px-1 items-center w-full"
      >
        <textarea
          defaultValue={initialPrompt}
          name="prompt"
          // onKeyDown={(e) => {
          //   if (e.key === "Enter") {
          //     e.preventDefault();
          //     submitRef.current?.click();
          //   }
          // }}
          onChange={(e) => {
            setPrompt(e.target.value);
          }}
          placeholder="Enter your prompt"
          className="bg-transparent text-white placeholder:text-gray-400 ring-0 outline-none resize-none py-2.5 px-2 font-mono text-sm h-20 w-full transition-all duration-300"
        />
        <input
          aria-hidden
          type="text"
          name="token"
          value={token}
          className="hidden"
          readOnly
        />
        <button
          type="submit"
          disabled={pending}
          aria-disabled={pending}
          onClick={async () => {
            setPending(true);
            setTexting(await getAnswer(prompt));
            console.log("Pending:", pending);
            console.log("PROMPT:", prompt);
            setPending(false);
            console.log("Pending:", pending);
            setRenderCount(renderCount + 1);
          }}
          className="text-white rounded-lg hover:bg-white/25 focus:bg-white/25 w-8 h-8 aspect-square flex items-center justify-center ring-0 outline-0"
        >
          {pending ? (
            <Loader />
          ) : (
            <CornerDownLeft size={16} className="-ml-px" />
          )}
        </button>
      </form>

      <Typer texting={texting} renderCount={renderCount} />
    </>
  );
}

interface TyperProps {
  texting: string;
  renderCount: number;
}
export function Typer({ texting, renderCount }: TyperProps) {
  const [typer, setTyper] = useState(<></>);
  if (!texting) {
    texting = "";
  }
  useEffect(() => {
    console.log("TEXT:", texting);

    setTyper(
      <>
        <div className="bg-transparent text-black placeholder:text-gray-400 ring-0 outline-none resize-none py-2.5 px-2 font-mono text-sm h-10 w-full transition-all duration-300">
          <Typewriter
            options={{
              strings: [texting],
              autoStart: true,
              loop: false,
              delay: 50,
            }}
          />
        </div>
      </>
    );
  }, [texting]);

  return <>{typer}</>;
}
