import React from 'react';
import PropTypes from 'prop-types';
import {shortDate} from 'utils';
import {getPicture, getThumbnailRendition, getCaption} from 'wire/utils';
import CardRow from './CardRow';
import {Embargo} from '../../../wire/components/fields/Embargo';

const getMediaPanel = (item: any, picture: any, openItem: any, cardId: any) => {

    const rendition = getThumbnailRendition(picture);
    const imageUrl = rendition && rendition.href;
    const caption = rendition && getCaption(picture);

    return (<div key={item._id} className='col-sm-6 col-lg-3 d-flex mb-4'>
        <div className='card card--home card--gallery' onClick={() => openItem(item, cardId)}>
            <img className='card-img-top' src={imageUrl} alt={caption} />
            <div className='card-body'>
                <div className='wire-articles__item__meta'>
                    <div className='wire-articles__item__meta-info'>
                        <span>{shortDate(item.versioncreated)}</span>
                    </div>
                </div>
                <h4 className='card-title'>{item.headline}</h4>
                <Embargo item={item} isCard={true} />
            </div>
        </div>
    </div>);
};

function MediaGalleryCard ({items, title, productId, openItem, isActive, cardId}: any) {
    return (
        <CardRow title={title} id={productId} isActive={isActive}>
            {items.map((item: any) => getMediaPanel(item, getPicture(item), openItem, cardId))}
        </CardRow>
    );
}

MediaGalleryCard.propTypes = {
    items: PropTypes.array,
    title: PropTypes.string,
    productId: PropTypes.string,
    openItem: PropTypes.func,
    isActive: PropTypes.bool,
    cardId: PropTypes.string,
};

export default MediaGalleryCard;
