import { useState } from 'react';

export default function NewsCard({newsStories, storyType}){
    const [failedImages, setFailedImages] = useState(new Set());

    const handleImageError = (storyTitle) => {
        setFailedImages(prev => new Set([...prev, storyTitle]));
    };

    return(
        <div>
          <aside className="mainTwo">
            <p className="section-label">{storyType}</p>
            {newsStories.length === 0 && (
              <p className="status-message">No national stories right now.</p>
            )}
            {newsStories.map((story) => (
              <div key={story.title} className="must-read-card">
                {story.imageUrl && !failedImages.has(story.title) && (
                  <img 
                    src={story.imageUrl} 
                    alt={story.title} 
                    width="280"
                    onError={() => handleImageError(story.title)}
                  />
                )}
                <h4> <a href={story.url}>{story.title}</a></h4>
                {(!story.imageUrl || failedImages.has(story.title)) && (
                  <p className="story-summary">{story.summary}</p>
                )}
              </div>
            ))}
            <hr />
          </aside>
        </div>
    )
}