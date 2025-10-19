import { useEffect, useState } from "react";
import { apiClient } from "../api/client";

export interface CardDefinition {
  id?: string;
  name?: string;
  type?: string;
  cost?: number;
  slo?: number;
  prerequisite?: string;
  effect?: string;
  repair?: string;
  stars?: number;
  action?: string;
}

interface ApiResponse {
  mode: string;
  cards: CardDefinition[];
}

export function useCardCatalog(mode: "classic" | "junior" = "classic") {
  const [cards, setCards] = useState<CardDefinition[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let ignore = false;
    async function fetchCards() {
      setLoading(true);
      try {
        const { data } = await apiClient.get<ApiResponse>("/cards", { params: { mode } });
        if (!ignore) setCards(data.cards);
      } finally {
        if (!ignore) setLoading(false);
      }
    }
    fetchCards();
    return () => {
      ignore = true;
    };
  }, [mode]);

  return { cards, loading };
}
