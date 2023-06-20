import React from 'react';
import PropTypes from 'prop-types';
import {getPicture, getThumbnailRendition, getCaption} from 'wire/utils';
import CardBody from './CardBody';
import CardFooter from './CardFooter';
import CardRow from './CardRow';

const getPictureTextPanel = (item, picture, openItem, withPictures, cardId, listConfig) => {
    const rendition = withPictures && getThumbnailRendition(picture);
    const imageUrl = rendition && rendition.href;
    const caption = rendition && getCaption(picture);

    return (<div key={item._id} className="col-sm-6 col-lg-4 col-xl-3 d-flex mb-4">
        <div className="card card--home" onClick={() => openItem(item, cardId)}>
            {rendition &&
                <div className="card-img-top-wrapper card-img-top-wrapper--aspect-16-9">
                    <img className="card-img-top" src={imageUrl} alt={caption} />
                </div>
            }
            <CardBody item={item} displayMeta={false} listConfig={listConfig} />
            <CardFooter
                item={item}
                picture={rendition}
                listConfig={listConfig}
            />
        </div>
    </div>);
};


function PictureTextCard ({type, items, title, productId, openItem, isActive, cardId, listConfig}) {
    const withPictures = type.indexOf('picture') > -1;

    return (
        <CardRow title={title} productId={productId} isActive={isActive}>
            {items.map((item) => getPictureTextPanel(item, getPicture(item), openItem, withPictures, cardId, listConfig))}
        </CardRow>
    );
}

PictureTextCard.propTypes = {
    type: PropTypes.string,
    items: PropTypes.array,
    title: PropTypes.string,
    productId: PropTypes.string,
    openItem: PropTypes.func,
    isActive: PropTypes.bool,
    cardId: PropTypes.string,
    listConfig: PropTypes.object,
};

export default PictureTextCard;
