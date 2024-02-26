import React from 'react';
import ArticlePicture from 'ui/components/ArticlePicture';
import ArticleMedia from 'ui/components/ArticleMedia';
import {isCustomRendition, isKilled} from 'wire/utils';
import {IArticle} from 'interfaces';

interface IProps {
  association: IArticle;
  item: IArticle;
  download: () => void;
}

export default function RenditionData({association, item, download}: IProps) {
    const key = association?.guid || '';
    if (association?.type === 'picture') {
        return (
            <ArticlePicture
                key={key}
                picture={association}
                isKilled={isKilled(item)}
                isCustomRendition={isCustomRendition(association)}
            />
        );
    }

    return (
        <ArticleMedia
            key={key}
            media={association}
            isKilled={isKilled(item)}
            download={download}
        />
    );
}