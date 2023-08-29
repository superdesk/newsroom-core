import React from 'react';
import {shortDate} from 'utils';
import {getPicture, getThumbnailRendition, getCaption} from 'wire/utils';
import CardRow from './CardRow';
import {Embargo} from '../../../wire/components/fields/Embargo';
import {ICardProps} from '../utils';

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

const MediaGalleryCard: React.ComponentType<ICardProps> = (props: ICardProps) => {
    const {items, title, id, openItem, isActive, cardId} = props;

    return (
        <CardRow title={title} id={id} isActive={isActive}>
            {items.map((item: any) => getMediaPanel(item, getPicture(item), openItem, cardId))}
        </CardRow>
    );
};

export default MediaGalleryCard;
