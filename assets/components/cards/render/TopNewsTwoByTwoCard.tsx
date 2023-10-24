import React from 'react';
import PropTypes from 'prop-types';

import {IArticle, IListConfig} from 'interfaces';

import {getSlugline} from 'utils';
import {getPicture, getThumbnailRendition, getCaption, shortText} from 'wire/utils';
import CardRow from './CardRow';
import CardFooter from './CardFooter';
import CardMeta from './CardMeta';
import CardBody from './CardBody';
import {Embargo} from '../../../wire/components/fields/Embargo';

const getTopNewsLeftPanel = (item: IArticle, picture: IArticle, openItem: any, cardId: string, listConfig: IListConfig) => {
    const rendition = getThumbnailRendition(picture, true);
    const imageUrl = rendition && rendition.href;
    const caption = rendition && getCaption(picture);

    return (<div key={item._id} className='col-sm-6 col-md-9 d-flex mb-4'>
        <div className='card card--home card--horizontal' onClick={() => openItem(item, cardId)}>
            {imageUrl && <div className='card-image-left'>
                <img src={imageUrl} alt={caption} />
            </div>}
            <div className='card-body'>
                <h2 className='card-title'>{item.headline}</h2>
                <Embargo item={item} isCard={true} />
                <CardMeta
                    item={item}
                    displayDivider={false}
                    slugline={getSlugline(item, true)}
                    listConfig={listConfig}
                />
                <div className='wire-articles__item__text'>
                    <p className='card-text'>{shortText(item, 40, listConfig)}</p>
                </div>
            </div>
        </div>
    </div>
    );
};

const getTopNewsRightPanel = (item: IArticle, picture: IArticle, openItem: any, cardId: string, listConfig?: IListConfig): any => {
    const rendition = getThumbnailRendition(picture);
    const imageUrl = rendition && rendition.href;
    const caption = rendition && getCaption(picture);

    return (<div key={item._id} className='col-sm-6 col-md-3 d-flex mb-4'>
        <div className='card card--home' onClick={() => openItem(item, cardId)}>
            {imageUrl == null ? null : (
                <img className='card-img-top' src={imageUrl} alt={caption} />
            )}
            <CardBody item={item} displayDescription={false} displaySource={false} listConfig={listConfig}/>
            <CardFooter item={item} />
        </div>
    </div>);
};

const getTopNews = (items: any, openItem: any, cardId: any, listConfig: any) => {
    const topNews: Array<any> = [];
    for(let i=0; i<items.length; i+=2) {
        topNews.push(getTopNewsLeftPanel(items[i], getPicture(items[i]), openItem, cardId, listConfig));
        if (i+1 < items.length) {
            topNews.push(getTopNewsRightPanel(items[i+1], getPicture(items[i+1]), openItem, cardId));
        }
    }
    return topNews;
};

function TopNewsTwoByTwoCard ({items, title, productId, openItem, isActive, cardId, listConfig}: any): any {
    return (
        <CardRow title={title} id={productId} isActive={isActive}>
            {getTopNews(items, openItem, cardId, listConfig)}
        </CardRow>
    );
}

TopNewsTwoByTwoCard.propTypes = {
    items: PropTypes.array,
    title: PropTypes.string,
    productId: PropTypes.string,
    openItem: PropTypes.func,
    isActive: PropTypes.bool,
    cardId: PropTypes.string,
    listConfig: PropTypes.object,
};

export default TopNewsTwoByTwoCard;
