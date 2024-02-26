import React from 'react';
import ArticlePicture from 'ui/components/ArticlePicture';
import ArticleMedia from 'ui/components/ArticleMedia';

export default function MediaPreview({
    data,
    isKilled,
    isCustomRendition,
    download,
}: any){
    const key = data?.guid;
    const type = data?.type;
    if (type === 'picture') {
        return (
            <ArticlePicture
                key={key}
                picture={data}
                isKilled={isKilled}
                isCustomRendition={isCustomRendition}
            />
        );
    }

    return (
        <ArticleMedia
            key={key}
            media={data}
            isKilled={isKilled}
            download={download}
        />
    );
}