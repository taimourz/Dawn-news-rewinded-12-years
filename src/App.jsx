import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { DataProvider } from './context/DataContext.jsx';
import Header from './components/Header/Header.jsx';
import Footer from './components/Footer/Footer.jsx';
import CategoryCard from './components/Category/CategoryCard.jsx';

function App() {
  return (
    <BrowserRouter basename={import.meta.env.BASE_URL}>
      <DataProvider>
        <div className="app-shell">
          <Header/>
          <Routes>
            <Route path="/" element={<CategoryCard category="front-page" />} />

            <Route path="/front-page" element={<CategoryCard category="latest" />} />
            <Route path="/national" element={<CategoryCard category="national" />} />
            <Route path="/international" element={<CategoryCard category="international" />} />
            <Route path="/business" element={<CategoryCard category="business" />} />
            <Route path="/business-finance" element={<CategoryCard category="business-finance" />} />
            <Route path="/sports" element={<CategoryCard category="sports" />} />
            <Route path="/letters" element={<CategoryCard category="letters" />} />
            <Route path="/other-voices" element={<CategoryCard category="other-voices" />} />
            <Route path="/editorial" element={<CategoryCard category="editorial" />} />
            <Route path="/back-page" element={<CategoryCard category="back-page" />} />
            <Route path="/sunday-magazine" element={<CategoryCard category="sunday-magazine" />} />
            <Route path="/icon" element={<CategoryCard category="icon" />} />
            <Route path="/young-world" element={<CategoryCard category="young-world" />} />

            <Route path="*" element={<CategoryCard category="front-page" />} />
          </Routes>

          <Footer />
        </div>
      </DataProvider>
    </BrowserRouter>
  );
}

export default App;