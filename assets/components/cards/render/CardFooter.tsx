import React from 'react';
import {IArticle, IListConfig} from 'interfaces';
import CardMeta from './CardMeta';

interface IProps {
    item: IArticle;
    listConfig?: IListConfig;
}

function CardFooter({item, listConfig}: IProps) {
    return (<div className="card-footer">
        <CardMeta
            item={item}
            listConfig={listConfig}
        />
    </div>);
}

export default CardFooter;
