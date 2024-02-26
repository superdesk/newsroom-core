import React from 'react';
import ArticlePicture from 'ui/components/ArticlePicture';
import ArticleMedia from 'ui/components/ArticleMedia';
import {isCustomRendition, isKilled} from 'wire/utils';
import {IArticle} from 'interfaces';

interface IProps {
  data: IArticle;
  item: IArticle;
  download: () => void;
}

export default function RenditionData({data, item, download}: IProps) {
    const key = data?.guid || '';
    if (data?.type === 'picture') {
        return (
            <ArticlePicture
                key={key}
                picture={data}
                isKilled={isKilled(item)}
                isCustomRendition={isCustomRendition(data)}
            />
        );
    }

    return (
        <ArticleMedia
            key={key}
            media={data}
            isKilled={isKilled(item)}
            download={download}
        />
    );
}