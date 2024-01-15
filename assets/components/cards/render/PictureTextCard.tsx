import React from 'react';
import {getPicture, getThumbnailRendition, getCaption} from 'wire/utils';
import CardBody from './CardBody';
import CardFooter from './CardFooter';
import CardRow from './CardRow';
import {ICardProps} from '../utils';
import {IArticle, IListConfig} from 'interfaces';

const getPictureTextPanel = (
    item: IArticle,
    picture: IArticle | null,
    openItem: ICardProps['openItem'],
    withPictures: boolean,
    cardId: ICardProps['cardId'],
    listConfig: IListConfig,
) => {
    const rendition = withPictures && picture != null && getThumbnailRendition(picture);
    const imageUrl = rendition && rendition.href;
    const caption = rendition && getCaption(picture);

    return (<div key={item._id} className="col-sm-6 col-lg-4 col-xl-3 d-flex mb-4">
        <div className="card card--home" onClick={() => openItem(item, cardId)}>
            {(rendition && imageUrl) ? (
                <div className="card-img-top-wrapper card-img-top-wrapper--aspect-16-9">
                    <img className="card-img-top" src={imageUrl} alt={caption} />
                </div>
            ) : null}
            <CardBody item={item} displayMeta={false} listConfig={listConfig} />
            <CardFooter
                item={item}
                listConfig={listConfig}
            />
        </div>
    </div>);
};

const PictureTextCard: React.ComponentType<ICardProps> = (props: ICardProps) => {
    const {type, items, title, id, openItem, isActive, cardId, listConfig, kind} = props;
    const withPictures = type.indexOf('picture') > -1;

    return (
        <CardRow kind={kind} title={title} id={id} isActive={isActive} onMoreNewsClicked={props.onMoreNewsClicked}>
            {items.map((item: any) => getPictureTextPanel(item, getPicture(item), openItem, withPictures, cardId, listConfig))}
        </CardRow>
    );
};

export default PictureTextCard;
