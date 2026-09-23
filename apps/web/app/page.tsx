import Link from "next/link";
import EventDiscovery from "./components/event-discovery";
import SourceManager from "./components/source-manager";

export default function Home() {
  return (
    <main className="site-shell">
      <nav className="nav"><Link className="brand" href="/">Feste <i>Italia</i></Link><div className="nav-links"><a href="#scopri">Scopri</a><a href="#idee">Idee per gite</a><a className="nav-action" href="#segnala">Segnala un evento</a></div></nav>
      <section className="hero">
        <div className="hero-copy"><p className="eyebrow">Il calendario che ti porta fuori casa</p><h1>Questo weekend,<br /><em>succede qualcosa.</em></h1><p className="hero-text">Sagre, feste di paese, mostre e piccoli tesori da scoprire. Tutto quello che accade in Italia, vicino a te.</p><form className="search" action="#scopri"><input aria-label="Cerca eventi o località" placeholder="Cerca una città, una regione, un evento..." /><button type="submit">Cerca <span>↗</span></button></form></div>
        <div className="hero-art"><div className="sun"></div><div className="land land-back"></div><div className="land land-front"></div><div className="art-label">Settembre<br /><strong>2026</strong></div></div>
      </section>
      <EventDiscovery />
      <section className="ideas" id="idee"><div><p className="eyebrow">Non solo eventi</p><h2>Hai voglia di partire,<br /><em>ma non sai dove?</em></h2></div><p>Itinerari, borghi e natura per trasformare una giornata libera in una piccola avventura.</p><a href="#idee">Esplora le idee <span>→</span></a></section>
      <SourceManager />
      <footer><span>© 2026 Feste Italia</span><span>Fatto per chi ama perdersi bene.</span></footer>
    </main>
  );
}
