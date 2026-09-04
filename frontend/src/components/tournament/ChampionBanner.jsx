import { useEffect, useState } from 'react';
import { getResult } from '../../api/matchApi';

export default function ChampionBanner({ tournament, matches, standings }) {
  const [knockoutChampion, setKnockoutChampion] = useState(null);

  useEffect(() => {
    async function findKnockoutChampion() {
      if (tournament.format !== 'KNOCKOUT' || matches.length === 0) return;
      const highestRoundNum = Math.max(
        ...matches.map((m) => {
          const match = m.round.match(/Round (\d+)/);
          return match ? parseInt(match[1], 10) : 0;
        })
      );
      const final = matches.find((m) => m.round.startsWith(`Round ${highestRoundNum}-`));
      if (!final || final.status !== 'COMPLETED') return;
      try {
        const res = await getResult(final.id);
        setKnockoutChampion(res.data.winner?.name || null);
      } catch {
        setKnockoutChampion(null);
      }
    }
    findKnockoutChampion();
  }, [tournament, matches]);

  if (tournament.status !== 'COMPLETED') return null;

  const champion =
    tournament.format === 'ROUND_ROBIN'
      ? standings[0]?.name
      : knockoutChampion;

  if (!champion) return null;

  return (
    <div className="bg-gradient-to-r from-accent to-accent-dark rounded-2xl p-6 mb-6 text-center">
      <p className="text-text-secondary text-sm mb-1">🏆 Champion</p>
      <h2 className="text-3xl text-text-primary font-bold">{champion}</h2>
    </div>
  );
}