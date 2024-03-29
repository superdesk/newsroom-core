import React, {ComponentType} from 'react';
import {IArticle, IListConfig} from 'interfaces';
import CardRow from './CardRow';
import CardFooter from './CardFooter';
import {shortText} from 'wire/utils';
import {Embargo} from '../../../wire/components/fields/Embargo';
import {ICardProps} from '../utils';

const getTextOnlyPanel = (item: IArticle, openItem: any, cardId: string, listConfig: IListConfig) => (
    <div key={item._id} className='col-sm-6 col-md-4 col-lg-3 col-xxl-2 d-flex mb-4'>
        <div className='card card--home' onClick={() => openItem(item, cardId)}>
            <div className='card-body'>
                <h4 className='card-title'>{item.headline}</h4>
                <Embargo item={item} isCard={true} />
                <div className='wire-articles__item__text'>
                    <p className='card-text small'>{shortText(item, 40, listConfig)}</p>
                </div>
            </div>
            <CardFooter
                item={item}
                listConfig={listConfig}
            />
        </div>
    </div>
);

const TextOnlyCard: ComponentType<ICardProps> = (props: ICardProps) => {
    const {items, title, id, openItem, isActive, cardId, listConfig} = props;

    return (
        <CardRow title={title} id={id} isActive={isActive} onMoreNewsClicked={props.onMoreNewsClicked}>
            {items.map((item: any) => getTextOnlyPanel(item, openItem, cardId, listConfig))}
        </CardRow>
    );
};

export default TextOnlyCard;
