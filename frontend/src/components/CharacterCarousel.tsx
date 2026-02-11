import { useState, useEffect, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { ChevronLeft, ChevronRight } from "lucide-react";
import CharacterCard from "./CharacterCard";
import type { HistoricalCharacter } from "@/data/characters";

interface CharacterCarouselProps {
  characters: HistoricalCharacter[];
  onSelect: (character: HistoricalCharacter) => void;
}

const VISIBLE_COUNT = 4;
const AUTO_INTERVAL = 10000;

const CharacterCarousel = ({ characters, onSelect }: CharacterCarouselProps) => {
  const [startIndex, setStartIndex] = useState(0);
  const maxStart = Math.max(0, characters.length - VISIBLE_COUNT);

  const goNext = useCallback(() => {
    setStartIndex((prev) => (prev >= maxStart ? 0 : prev + 1));
  }, [maxStart]);

  const goPrev = useCallback(() => {
    setStartIndex((prev) => (prev <= 0 ? maxStart : prev - 1));
  }, [maxStart]);

  useEffect(() => {
    const timer = setInterval(goNext, AUTO_INTERVAL);
    return () => clearInterval(timer);
  }, [goNext]);

  const visibleCharacters = characters.slice(startIndex, startIndex + VISIBLE_COUNT);
  // Handle wrapping when near the end
  if (visibleCharacters.length < VISIBLE_COUNT) {
    const remaining = VISIBLE_COUNT - visibleCharacters.length;
    visibleCharacters.push(...characters.slice(0, remaining));
  }

  return (
    <div className="relative group">
      {/* Left arrow */}
      <button
        onClick={goPrev}
        className="absolute -left-4 md:-left-6 top-1/2 -translate-y-1/2 z-10 p-2 rounded-full bg-card/80 border border-border backdrop-blur-sm text-muted-foreground hover:text-foreground hover:border-primary/50 transition-all opacity-0 group-hover:opacity-100 duration-300"
        aria-label="Previous"
      >
        <ChevronLeft size={24} />
      </button>

      {/* Cards */}
      <div className="overflow-hidden">
        <AnimatePresence mode="popLayout">
          <motion.div
            key={startIndex}
            initial={{ opacity: 0, x: 60 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -60 }}
            transition={{ duration: 0.4, ease: "easeInOut" }}
            className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4"
          >
            {visibleCharacters.map((char, i) => (
              <CharacterCard
                key={char.id}
                character={char}
                onClick={onSelect}
                index={i}
              />
            ))}
          </motion.div>
        </AnimatePresence>
      </div>

      {/* Right arrow */}
      <button
        onClick={goNext}
        className="absolute -right-4 md:-right-6 top-1/2 -translate-y-1/2 z-10 p-2 rounded-full bg-card/80 border border-border backdrop-blur-sm text-muted-foreground hover:text-foreground hover:border-primary/50 transition-all opacity-0 group-hover:opacity-100 duration-300"
        aria-label="Next"
      >
        <ChevronRight size={24} />
      </button>

      {/* Dots indicator */}
      <div className="flex justify-center gap-1.5 mt-6">
        {Array.from({ length: maxStart + 1 }, (_, i) => (
          <button
            key={i}
            onClick={() => setStartIndex(i)}
            className={`w-2 h-2 rounded-full transition-all duration-300 ${
              i === startIndex
                ? "bg-primary w-6"
                : "bg-muted-foreground/30 hover:bg-muted-foreground/60"
            }`}
            aria-label={`Go to slide ${i + 1}`}
          />
        ))}
      </div>
    </div>
  );
};

export default CharacterCarousel;
