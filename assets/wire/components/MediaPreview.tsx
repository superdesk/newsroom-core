import React from 'react';
import ArticlePicture from 'ui/components/ArticlePicture';
import ArticleMedia from 'ui/components/ArticleMedia';
import {isCustomRendition, isKilled} from 'wire/utils';
import {IArticle} from 'interfaces';

interface IProps {
    media: IArticle;
    item: IArticle;
    download: () => void;
}

export default function MediaPreview({media, item, download}: IProps) {
    const key = media?.guid || '';
    if (media?.type === 'picture') {
        return (
            <ArticlePicture
                key={key}
                picture={media}
                isKilled={isKilled(item)}
                isCustomRendition={isCustomRendition(media)}
            />
        );
    }

    return (
        <ArticleMedia
            key={key}
            media={media}
            isKilled={isKilled(item)}
            download={download}
        />
    );
}