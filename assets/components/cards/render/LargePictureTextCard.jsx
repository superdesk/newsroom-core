import React from 'react';
import PropTypes from 'prop-types';
import {getCaption, getPicture, getThumbnailRendition} from 'wire/utils';
import CardFooter from './CardFooter';
import CardBody from './CardBody';
import CardRow from './CardRow';

const getPictureTextPanel = (item, picture, openItem, cardId, listConfig) => {
    const rendition = getThumbnailRendition(picture);
    const imageUrl = rendition && rendition.href;
    const caption = rendition && getCaption(picture);

    return (<div key={item._id} className="col-sm-6 col-lg-4 d-flex mb-4">
        <div className="card card--home" onClick={() => openItem(item, cardId)}>
            {rendition &&
                <div className="card-img-top-wrapper card-img-top-wrapper--aspect-16-9">
                    <img className="card-img-top" src={imageUrl} alt={caption} />
                </div>
            }
            <CardBody item={item} displaySource={false} listConfig={listConfig} />
            <CardFooter
                item={item}
                picture={picture}
                listConfig={listConfig}
            />
        </div>
    </div>);
};

function LargePictureTextCard ({items, title, productId, openItem, isActive, cardId, listConfig}) {
    return (
        <CardRow title={title} productId={productId} isActive={isActive}>
            {items.map((item) => getPictureTextPanel(item, getPicture(item), openItem, cardId, listConfig))}
        </CardRow>
    );
}

LargePictureTextCard.propTypes = {
    items: PropTypes.array,
    title: PropTypes.string,
    productId: PropTypes.string,
    openItem: PropTypes.func,
    isActive: PropTypes.bool,
    cardId: PropTypes.string,
    listConfig: PropTypes.object,
};

export default LargePictureTextCard;
