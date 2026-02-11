import hannibalImg from "@/assets/hannibal.jpg";
import hamilcarImg from "@/assets/hamilcar.jpg";
import uqbaImg from "@/assets/uqba.jpg";
import ibnKhaldounImg from "@/assets/ibn-khaldoun.jpg";
import elyssaImg from "@/assets/elyssa.jpg";
import kahinaImg from "@/assets/kahina.jpg";
import kheireddineImg from "@/assets/kheireddine.jpg";
import farhatImg from "@/assets/farhat-hached.jpg";
import abuZakariyaImg from "@/assets/abu-zakariya.jpg";

export interface HistoricalCharacter {
  id: string;
  name: string;
  title: string;
  era: string;
  image: string;
  greeting: string;
  suggestedQuestions: string[];
}

export const characters: HistoricalCharacter[] = [
  {
    id: "hannibal",
    name: "Hannibal Barca",
    title: "Carthaginian General",
    era: "247 – 183 BC",
    image: hannibalImg,
    greeting: "I am Hannibal Barca, son of Hamilcar. I crossed the Alps with war elephants and brought Rome to its knees at Cannae. Ask me anything about strategy, war, or the fate of Carthage.",
    suggestedQuestions: [
      "Why did Carthage fall?",
      "How did you cross the Alps with elephants?",
      "What was your greatest military mistake?",
      "What would you do differently against Rome today?",
    ],
  },
  {
    id: "hamilcar",
    name: "Hamilcar Barca",
    title: "Carthaginian Commander",
    era: "275 – 228 BC",
    image: hamilcarImg,
    greeting: "I am Hamilcar Barca, father of Hannibal, commander of Carthage. I fought Rome in Sicily and built our empire in Iberia. Ask me of war, duty, and the Barcid legacy.",
    suggestedQuestions: [
      "How did you fight Rome in the First Punic War?",
      "Why did you conquer Iberia?",
      "What did you teach your sons about Rome?",
      "What was your vision for Carthage?",
    ],
  },
  {
    id: "elyssa",
    name: "Elyssa (Dido)",
    title: "Founder of Carthage",
    era: "c. 839 BC",
    image: elyssaImg,
    greeting: "I am Elyssa, whom the Romans call Dido. I fled Tyre, crossed the sea, and founded Carthage with nothing but courage and cunning. What do you wish to know?",
    suggestedQuestions: [
      "How did you found Carthage?",
      "What is the story of the ox hide?",
      "Why did you flee Tyre?",
      "What was your vision for the new city?",
    ],
  },
  {
    id: "uqba",
    name: "Uqba ibn Nafi",
    title: "Arab Conqueror of Ifriqiya",
    era: "622 – 683 AD",
    image: uqbaImg,
    greeting: "I am Uqba ibn Nafi, founder of Kairouan and bearer of Islam to the Maghreb. I rode to the Atlantic shore and declared there was no more land to conquer. Ask me of faith and conquest.",
    suggestedQuestions: [
      "Why did you found Kairouan?",
      "What was your famous declaration at the Atlantic?",
      "How did you spread Islam across North Africa?",
      "What challenges did you face from the Berbers?",
    ],
  },
  {
    id: "kahina",
    name: "Kahina",
    title: "Amazigh Warrior Queen",
    era: "7th century AD",
    image: kahinaImg,
    greeting: "I am Kahina, queen of the Imazighen. I united the Berber tribes and fought against the Umayyad conquest. My people called me a prophetess. What would you ask of me?",
    suggestedQuestions: [
      "How did you resist the Arab conquest?",
      "What was life like for the Berber tribes?",
      "Why are you called a prophetess?",
      "What happened after your last battle?",
    ],
  },
  {
    id: "ibn-khaldoun",
    name: "Ibn Khaldoun",
    title: "Father of Sociology",
    era: "1332 – 1406 AD",
    image: ibnKhaldounImg,
    greeting: "I am Ibn Khaldoun of Tunis, historian and scholar. I wrote the Muqaddimah to understand why civilizations rise and fall. Ask me about history, society, or the nature of power.",
    suggestedQuestions: [
      "What is the Muqaddimah about?",
      "Why do civilizations rise and fall?",
      "What is Asabiyyah?",
      "How did Tunis shape your thinking?",
    ],
  },
  {
    id: "abu-zakariya",
    name: "Abu Zakariya Yahya",
    title: "Founder of the Hafsid Dynasty",
    era: "1203 – 1249 AD",
    image: abuZakariyaImg,
    greeting: "I am Abu Zakariya Yahya, founder of the Hafsid dynasty and Sultan of Ifriqiya. I made Tunis the capital of a great kingdom and a center of learning. What do you wish to know?",
    suggestedQuestions: [
      "How did you establish the Hafsid dynasty?",
      "What made Tunis a great capital?",
      "How did you manage relations with the Almohads?",
      "What was your legacy for Tunisia?",
    ],
  },
  {
    id: "kheireddine",
    name: "Kheireddine Pacha",
    title: "Ottoman Admiral & Corsair",
    era: "1478 – 1546 AD",
    image: kheireddineImg,
    greeting: "I am Kheireddine, whom the Christians call Barbarossa. I commanded the Ottoman fleet, liberated Muslim captives, and made the Mediterranean tremble. What do you seek?",
    suggestedQuestions: [
      "How did you become ruler of Algiers?",
      "What was the Battle of Preveza like?",
      "How did you build the Ottoman navy?",
      "What was your relationship with Suleiman the Magnificent?",
    ],
  },
  {
    id: "farhat-hached",
    name: "Farhat Hached",
    title: "Trade Union Leader & Martyr",
    era: "1914 – 1952 AD",
    image: farhatImg,
    greeting: "I am Farhat Hached, founder of the UGTT and fighter for Tunisia's independence. I believed that the liberation of workers and the liberation of the nation were one and the same. Ask me about our struggle.",
    suggestedQuestions: [
      "Why did you found the UGTT?",
      "How did the labor movement help Tunisian independence?",
      "Who was behind your assassination?",
      "What was your vision for a free Tunisia?",
    ],
  },
];
