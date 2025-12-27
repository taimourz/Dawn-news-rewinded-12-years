import { useData } from '../../context/DataContext.jsx';
import NewsCard from '../NewsCard/NewsCard.jsx';
import './CategoryCard.css';

export default function CategoryCard({ category }) {
    const { 
        getFrontPageStories,
        getSportStories,
        getBusinessStories,
        getInternationalStories,
        getSundayMagzineStories,
        getNationalStories,
        getBackPageStories,
        getOtherVoicesStories,
        getLettersStories,
        getBooksAuthorsStories,
        getBusinessFinanceStories,
        getYoungWorldStories,
        getIconStories,
        getEditorialStories,
        isLoadingArchive
    } = useData();

    const categoryFunctions = {
        'latest': getFrontPageStories,
        'sports': getSportStories,
        'business': getBusinessStories,
        'international': getInternationalStories, 
        'sunday-magazine': getSundayMagzineStories,
        'national': getNationalStories,
        'back-page': getBackPageStories,
        'other-voices': getOtherVoicesStories,
        'letters': getLettersStories,
        'books-authors': getBooksAuthorsStories,
        'business-finance': getBusinessFinanceStories,
        'young-world': getYoungWorldStories,
        'icon': getIconStories,
        'editorial': getEditorialStories
    };

    const categoryNames = {
        'front-page': 'Front Page',
        'latest': 'Latest',
        'sports': 'Sports',
        'business': 'Business',
        'magazines': 'Magazines',
        'national': 'National',
        'back-page': 'Back Page',
        'other-voices': 'Other Voices',
        'letters': 'Letters',
        'books-authors': 'Books & Authors',
        'business-finance': 'Business & Finance',
        'editorial': 'Editorial',
        'sunday-magazine': 'Sunday Magazine',
        'young-world': 'Young World',
        'icon': 'Icon'
    };

    if (isLoadingArchive) { 
        return <div style={{textAlign: 'center', padding: '40px'}}>Loading...</div>;
    }

    const getStoriesFunction = categoryFunctions[category];
    
    if (!getStoriesFunction) {
        return (
            <div style={{textAlign: 'center', padding: '40px'}}>
                <h2>Category "{categoryNames[category] || category}" not found</h2>
                <p>This section is not available yet.</p>
            </div>
        );
    }

    const stories = getStoriesFunction();

    if (!stories || stories.length === 0) {
        return (
            <div style={{textAlign: 'center', padding: '40px'}}>
                <h2>{categoryNames[category]}</h2>
                <p>No stories available for this section.</p>
            </div>
        );
    }

    return (
        <div className="category-container">
            <div className="category-header">
                <h1 className="category-title">{categoryNames[category]}</h1>
            </div>
            <div className="category-grid">
                {stories.map((story, index) => (
                    <NewsCard key={index} newsStories={[story]} storyType="" />
                ))}
            </div>
        </div>
    );
}