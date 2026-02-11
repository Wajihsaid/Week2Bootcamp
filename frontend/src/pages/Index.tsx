import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import CharacterCarousel from "@/components/CharacterCarousel";
import ChatInterface from "@/components/ChatInterface";
import { characters, type HistoricalCharacter } from "@/data/characters";
import heroBg from "@/assets/hero-bg.jpg";

const Index = () => {
  const [selectedCharacter, setSelectedCharacter] = useState<HistoricalCharacter | null>(null);

  if (selectedCharacter) {
    return (
      <div className="fixed inset-0 w-full h-full overflow-hidden">
        <AnimatePresence mode="wait">
          <ChatInterface
            key={selectedCharacter.id}
            character={selectedCharacter}
            onBack={() => setSelectedCharacter(null)}
          />
        </AnimatePresence>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-dark">
      {/* Hero */}
      <div className="relative h-[60vh] min-h-[400px] flex items-center justify-center overflow-hidden">
        <img
          src={heroBg}
          alt="Ancient ruins"
          className="absolute inset-0 w-full h-full object-cover opacity-40"
        />
        <div className="absolute inset-0 bg-gradient-to-b from-background/30 via-transparent to-background" />
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="relative text-center px-6"
        >
          <p className="text-xs font-sans uppercase tracking-[0.3em] text-primary mb-4">
            Talk to the Past with AI
          </p>
          <h1 className="text-5xl md:text-7xl font-display font-bold text-gradient-gold mb-4">
            Echoes of History
          </h1>
          <p className="text-lg text-muted-foreground max-w-xl mx-auto font-body">
            Step into conversations with history's greatest figures. Ask questions,
            hear their stories — told in their own words.
          </p>
        </motion.div>
      </div>

      {/* Characters Carousel */}
      <div className="relative -mt-16 px-10 md:px-16 pb-16">
        <div className="max-w-5xl mx-auto">
          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.4 }}
            className="text-xs font-sans uppercase tracking-[0.2em] text-muted-foreground mb-6 text-center"
          >
            Choose a figure to begin
          </motion.p>
          <CharacterCarousel characters={characters} onSelect={setSelectedCharacter} />
        </div>
      </div>
    </div>
  );
};

export default Index;