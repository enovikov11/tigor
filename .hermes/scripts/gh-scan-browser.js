// GitHub org + repo scanner — paste in browser console (F12 → Console)
// Requires PAT with repo + read:org scope
(async () => {
  const t = prompt('GitHub PAT:');
  const h = { Authorization: `Bearer ${t}`, Accept: 'application/vnd.github+json' };
  const all = [];
  const pg = u => (async () => { for (let p = 1;; ++p) { const j = await fetch(`${u}?per_page=100&page=${p}`, { headers: h }).then(r => r.json()); if (!j.length) break; all.push(...j); } })();

  await pg('https://api.github.com/user/repos');
  const orgs = await fetch('https://api.github.com/user/orgs', { headers: h }).then(r => r.json());
  for (const o of orgs) await pg(`https://api.github.com/orgs/${o.login}/repos`);

  const rows = all.map(r => ({
    repo: r.full_name,
    fork: r.fork ? '🍴' : '',
    vis: r.private ? '🔒' : '🌐',
    parent: r.parent?.full_name || '—',
    lang: r.language || '',
    stars: r.stargazers_count || 0,
    updated: r.updated_at.slice(0, 10)
  }));

  console.clear();
  console.log(`\n  ${orgs.map(o => o.login).join(', ') || 'no orgs'}  |  ${rows.length} repos total\n`);
  console.table(rows, ['repo', 'fork', 'vis', 'parent', 'lang', 'stars', 'updated']);
  return rows;
})();
