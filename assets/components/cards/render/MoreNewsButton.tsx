import React from 'react';
import {gettext} from 'utils';

interface IProps {
    title: string;
    photoUrl?: string;
    kind: MoreNewsSearchKind;
    id?: string;
    photoUrlLabel?: string;
    moreNews?: boolean;
    onMoreNewsClicked?(event: React.MouseEvent<HTMLAnchorElement>): void;
}

export type MoreNewsSearchKind = 'product' | 'topic';
type MoreNewsInternalType = {[Property in MoreNewsSearchKind]: React.ComponentType<{
    id: string;
    onMoreNewsClicked?(event: React.MouseEvent<HTMLAnchorElement>): void;
}>;};

const MoreNewsInternal: MoreNewsInternalType = {
    'product': (props: {id: string, onMoreNewsClicked?(event: React.MouseEvent<HTMLAnchorElement>): void}) => (
        <a
            href={`/wire?product=${props.id}`}
            role='button'
            className='nh-button nh-button--tertiary nh-button--small mb-3'
            onClick={props.onMoreNewsClicked}
        >
            {gettext('More news')}
        </a>
    ),
    'topic':  (props: {id: string, onMoreNewsClicked?(event: React.MouseEvent<HTMLAnchorElement>): void}) => (
        <a
            href={`/wire?topic=${props.id}`}
            role='button'
            className='nh-button nh-button--tertiary nh-button--small mb-3'
            onClick={props.onMoreNewsClicked}
        >
            {gettext('More news')}
        </a>
    ),
};

function MoreNewsButton(props: IProps): any {
    const {title, photoUrl, photoUrlLabel, moreNews, kind, id} = props;
    const MoreNewsLink = MoreNewsInternal[kind];

    return (
        [
            <div key='heading' className='col-6 col-sm-8'>
                <h3 className='home-section-heading'>{title}</h3>
            </div>,
            <div key='more-news' className='col-6 col-sm-4 d-flex align-items-start justify-content-end'>
                {moreNews && id && <MoreNewsLink id={id} onMoreNewsClicked={props.onMoreNewsClicked} />}
                {photoUrl && (
                    <a href={photoUrl} target='_blank' rel='noopener noreferrer' role='button' className='nh-button nh-button--tertiary nh-button--small mb-3'>
                        {photoUrlLabel || photoUrl}
                    </a>
                )}
            </div>
        ]
    );
}

const component: React.ComponentType<IProps> = MoreNewsButton;

export default component;
