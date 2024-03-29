import React from 'react';
import {IArticle, IListConfig} from 'interfaces';
import {getPicture, getThumbnailRendition, getCaption, shortText} from 'wire/utils';
import CardRow from './CardRow';
import CardMeta from './CardMeta';
import {Embargo} from '../../../wire/components/fields/Embargo';
import {ICardProps} from '../utils';

const getTopNewsPanel = (item: IArticle, picture: IArticle | null, openItem: any, cardId: string, listConfig: IListConfig) => {
    const rendition = picture ? getThumbnailRendition(picture, true) : null;
    const imageUrl = rendition && rendition.href;
    const caption = rendition && getCaption(picture);

    return (<div key={item._id} className='col-sm-12 col-md-6 d-flex mb-4'>
        <div className='card card--home' onClick={() => openItem(item, cardId)}>
            {imageUrl == null ? null : (
                <img className='card-img-top' src={imageUrl} alt={caption} />
            )}
            <div className='card-body'>
                <h4 className='card-title'>{item.headline}</h4>
                <Embargo item={item} isCard={true} />
                <CardMeta
                    item={item}
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

const TopNewsOneByOneCard: React.ComponentType<ICardProps> = (props: ICardProps) => {
    const {items, title, id, openItem, isActive, cardId, listConfig} = props;

    return (
        <CardRow title={title} id={id} isActive={isActive} onMoreNewsClicked={props.onMoreNewsClicked}>
            {items.map((item: any) => getTopNewsPanel(item, getPicture(item), openItem, cardId, listConfig))}
        </CardRow>
    );
};

export default TopNewsOneByOneCard;
