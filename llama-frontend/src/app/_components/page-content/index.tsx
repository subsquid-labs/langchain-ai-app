import { Suspense } from "react";
import { EmojiGrid } from "../emoji-grid";
import { EmojiCount } from "../emoji-count";
import { EmojiForm } from "../emoji-form";

interface PageContentProps extends React.PropsWithChildren {
  prompt?: string;
}

export const PageContent = ({ children, prompt }: PageContentProps) => {
  return (
    <>
      <div className="py-[15vh] sm:py-[20vh] flex flex-col items-center justify-center">
        <h1 className="font-medium text-4xl text-black mb-2 animate-in fade-in slide-in-from-bottom-3 duration-1000 ease-in-out">
          Swap Transactions on UniswapV3
        </h1>

        {/* <EmojiCount /> */}

        <div className="max-w-md space-y-4 w-full animate-in fade-in slide-in-from-bottom-4 duration-1200 ease-in-out">
          <div className="rounded-xl h-fit flex flex-row px-1 items-center w-full pb-2 lg:mb-12 mb-16">
            <div className="bg-transparent text-gray-400 ring-0 outline-none resize-none py-2.5 px-2 font-mono text-xs h-20 w-full transition-all duration-300">
              Suggested prompts:
              <br /> 1. Which tools do you have?
              <br /> 2.Show me 10 swaps with amount0, amount1 and id. Use limit
              instead of first.
              <br /> 3.Which entities does the schema of the API have?
              <br />
              <div className="text-xs">
                Note: This website is a work in progress. More tools will be
                added. Drop me a line on Twitter for feature requests.
              </div>
            </div>
          </div>
          <div className="lg:h-0 h-2"> </div>
          <EmojiForm initialPrompt={prompt} />
          {children}
        </div>
      </div>
      {/* 
      <Suspense>
        <EmojiGrid prompt={prompt} />
      </Suspense> */}
    </>
  );
};
