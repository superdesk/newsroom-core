import React from 'react';
import CardFooter from './CardFooter';
import CardBody from './CardBody';
import CardRow from './CardRow';
import {getPicture} from 'wire/utils';
import {ICardProps} from '../utils';

const getTextOnlyPanel = (item: any, openItem: any, cardId: any, listConfig: any) => (
    <div key={item._id} className='col-sm-6 col-lg-4 d-flex mb-4'>
        <div className='card card--home' onClick={() => openItem(item, cardId)}>
            <CardBody item={item} displaySource={false} listConfig={listConfig} />
            <CardFooter
                item={item}
                picture={getPicture(item)}
                listConfig={listConfig}
            />
        </div>
    </div>
);

const LargeTextOnlyCard: React.ComponentType<ICardProps> = (props: ICardProps) => {
    const {items, title, id, openItem, isActive, cardId, listConfig} = props;

    return (
        <CardRow title={title} id={id} isActive={isActive}>
            {items.map((item) => getTextOnlyPanel(item, openItem, cardId, listConfig))}
        </CardRow>
    );
};

export default LargeTextOnlyCard;
