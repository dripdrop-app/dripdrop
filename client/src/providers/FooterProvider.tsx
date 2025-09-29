import { MutableRefObject, ReactNode, createContext, useContext, useRef, useState } from "react";

interface FooterContextType {
  displayFooter: boolean;
  setDisplayFooter: (displayFooter: boolean) => void;
  footerRef: MutableRefObject<HTMLDivElement | null>;
}

const FooterContext = createContext<FooterContextType | undefined>(undefined);

export const FooterProvider = ({ children }: { children: ReactNode }) => {
  const [displayFooter, setDisplayFooter] = useState(false);
  const footerRef = useRef<HTMLDivElement | null>(null);

  return (
    <FooterContext.Provider
      value={{
        displayFooter,
        setDisplayFooter,
        footerRef,
      }}
    >
      {children}
    </FooterContext.Provider>
  );
};

export const useFooter = () => {
  const context = useContext(FooterContext);
  if (context === undefined) {
    throw new Error("useFooter must be used within a FooterProvider");
  }
  return context;
};
