import React from 'react';
import PropTypes from 'prop-types';
import {getPicture, getThumbnailRendition, getCaption, shortText} from 'wire/utils';
import CardRow from './CardRow';
import CardMeta from './CardMeta';
import {Embargo} from '../../../wire/components/fields/Embargo';

const getTopNewsPanel = (item: any, picture: any, openItem: any, cardId: any, listConfig: any) => {

    const rendition = getThumbnailRendition(picture, true);
    const imageUrl = rendition && rendition.href;
    const caption = rendition && getCaption(picture);

    return (<div key={item._id} className='col-sm-12 col-md-6 d-flex mb-4'>
        <div className='card card--home' onClick={() => openItem(item, cardId)}>
            <img className='card-img-top' src={imageUrl} alt={caption} />
            <div className='card-body'>
                <h4 className='card-title'>{item.headline}</h4>
                <Embargo item={item} isCard={true} />
                <CardMeta
                    item={item}
                    picture={picture}
                    listConfig={listConfig}
                    displayDivider={false}
                />
                <div className='wire-articles__item__text'>
                    <p className='card-text small'>{shortText(item, 40, listConfig)}</p>
                </div>
            </div>
        </div>
    </div>);
};

function TopNewsOneByOneCard ({items, title, product, openItem, isActive, cardId, listConfig}: any) {
    return (
        <CardRow title={title} product={product} isActive={isActive}>
            {items.map((item: any) => getTopNewsPanel(item, getPicture(item), openItem, cardId, listConfig))}
        </CardRow>
    );
}

TopNewsOneByOneCard.propTypes = {
    items: PropTypes.array,
    title: PropTypes.string,
    product: PropTypes.object,
    openItem: PropTypes.func,
    isActive: PropTypes.bool,
    cardId: PropTypes.string,
    listConfig: PropTypes.object,
};

export default TopNewsOneByOneCard;
