import React from 'react';
import {getPicture, getThumbnailRendition, getCaption} from 'wire/utils';
import CardBody from './CardBody';
import CardFooter from './CardFooter';
import CardRow from './CardRow';
import {IPropsRest} from '../utils';

const getPictureTextPanel = (item: any, picture: any, openItem: any, withPictures: any, cardId: any, listConfig: any) => {
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

const PictureTextCard: React.ComponentType<IPropsRest> = (props: IPropsRest) => {
    const {type, items, title, id, openItem, isActive, cardId, listConfig, kind} = props;
    const withPictures = type.indexOf('picture') > -1;

    return (
        <CardRow kind={kind} title={title} id={id} isActive={isActive}>
            {items.map((item: any) => getPictureTextPanel(item, getPicture(item), openItem, withPictures, cardId, listConfig))}
        </CardRow>
    );
};

export default PictureTextCard;
