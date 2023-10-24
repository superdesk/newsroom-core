import React from 'react';
import {IArticle, IListConfig} from 'interfaces';

import {getCaption, getPicture, getThumbnailRendition} from 'wire/utils';
import CardFooter from './CardFooter';
import CardBody from './CardBody';
import CardRow from './CardRow';
import {ICardProps} from '../utils';

const getPictureTextPanel = (item: IArticle, picture: IArticle, openItem: any, cardId: string, listConfig: IListConfig) => {
    const rendition = getThumbnailRendition(picture);
    const imageUrl = rendition && rendition.href;
    const caption = rendition && getCaption(picture);

    return (<div key={item._id} className="col-sm-6 col-lg-4 d-flex mb-4">
        <div className="card card--home" onClick={() => openItem(item, cardId)}>
            {imageUrl != null &&
                <div className="card-img-top-wrapper card-img-top-wrapper--aspect-16-9">
                    <img className="card-img-top" src={imageUrl} alt={caption} />
                </div>
            }
            <CardBody item={item} displaySource={false} listConfig={listConfig} />
            <CardFooter
                item={item}
                listConfig={listConfig}
            />
        </div>
    </div>);
};

const LargePictureTextCard: React.ComponentType<ICardProps> = (props: ICardProps) => {
    const {items, title, id, openItem, isActive, cardId, listConfig} = props;

    return (
        <CardRow title={title} id={id} isActive={isActive}>
            {items.map((item) => getPictureTextPanel(item, getPicture(item), openItem, cardId, listConfig))}
        </CardRow>
    );
};

export default LargePictureTextCard;
