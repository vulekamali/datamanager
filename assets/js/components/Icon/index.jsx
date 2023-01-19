import Close from './partials/Close.jsx';
import Download from './partials/Download.jsx';
import Facebook from './partials/Facebook.jsx';
import Search from './partials/Search.jsx';
import Twitter from './partials/Twitter.jsx';
import Home from './partials/Home.jsx';
import Play from './partials/Play.jsx';
import Hamburger from './partials/Hamburger.jsx';
import Pin from './partials/Pin.jsx';
import Date from './partials/Date.jsx';
import Dataset from './partials/Dataset.jsx';
import Guide from './partials/Guide.jsx';


export default function Icon({ size, type }) {
  switch (type) {
    case 'close': return <Close {...{ size }} />;
    case 'download': return <Download {...{ size }} />;
    case 'facebook': return <Facebook {...{ size }} />;
    case 'search': return <Search {...{ size }} />;
    case 'twitter': return <Twitter {...{ size }} />;
    case 'play': return <Play {...{ size }} />;
    case 'home': return <Home {...{ size }} />;
    case 'hamburger': return <Hamburger {...{ size }} />;
    case 'pin': return <Pin {...{ size }} />;
    case 'date': return <Date {...{ size }} />;
    case 'dataset': return <Dataset {...{ size }} />;
    case 'guide': return <Guide {...{ size }} />;
    default: return null;
  }
}