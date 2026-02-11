import { motion } from "framer-motion";
import type { HistoricalCharacter } from "@/data/characters";

interface CharacterCardProps {
  character: HistoricalCharacter;
  onClick: (character: HistoricalCharacter) => void;
  index: number;
}

const CharacterCard = ({ character, onClick, index }: CharacterCardProps) => {
  return (
    <motion.button
      initial={{ opacity: 0, y: 30 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: index * 0.1 }}
      whileHover={{ scale: 1.03, y: -4 }}
      whileTap={{ scale: 0.98 }}
      onClick={() => onClick(character)}
      className="group relative overflow-hidden rounded-lg bg-gradient-card border border-border hover:border-primary/50 transition-colors duration-300 text-left"
    >
      <div className="relative aspect-[3/4] overflow-hidden">
        <img
          src={character.image}
          alt={character.name}
          className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-110"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-background via-background/40 to-transparent" />
      </div>
      <div className="absolute bottom-0 left-0 right-0 p-5">
        <p className="text-xs font-sans uppercase tracking-[0.2em] text-primary mb-1">
          {character.era}
        </p>
        <h3 className="text-xl font-display font-bold text-foreground mb-0.5">
          {character.name}
        </h3>
        <p className="text-sm text-muted-foreground">{character.title}</p>
      </div>
      <div className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none rounded-lg glow-gold" />
    </motion.button>
  );
};

export default CharacterCard;
