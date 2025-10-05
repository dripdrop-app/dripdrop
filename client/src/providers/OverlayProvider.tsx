import { createContext, ReactNode, useRef, MutableRefObject, useContext } from "react";

interface OverlayContextType {
  overlayRef: MutableRefObject<HTMLDivElement | null>;
}

const OverlayContext = createContext<OverlayContextType | undefined>(undefined);

export const OverlayProvider = ({ children }: { children: ReactNode }) => {
  const overlayRef = useRef<HTMLDivElement | null>(null);

  return (
    <OverlayContext.Provider
      value={{
        overlayRef,
      }}
    >
      {children}
    </OverlayContext.Provider>
  );
};

export const useOverlay = () => {
  const context = useContext(OverlayContext);

  if (context === undefined) {
    throw new Error("useOverlay must be used within a OverlayProvider");
  }
  return context;
};
