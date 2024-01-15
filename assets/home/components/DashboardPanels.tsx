import * as React from 'react';

import {IArticle, IDashboardCard, IListConfig} from 'interfaces';
import {gettext} from 'utils';

import {getCard} from 'components/cards/utils';
import CardRow from 'components/cards/render/CardRow';


interface IProps {
    cards: Array<IDashboardCard>;
    activeCard?: IDashboardCard['_id'];
    itemsByCard: {[cardId: string]: Array<IArticle>};
    listConfig: IListConfig;
    fetchCardItems?(): Promise<void>;
    fetchCardExternalItems(cardId: IDashboardCard['_id'], cardLabel: IDashboardCard['label']): void;
    openItem(item: IArticle, cardId: IDashboardCard['_id']): void;
    onMoreNewsClicked?(event: React.MouseEvent<HTMLAnchorElement>): void;
}

interface IState {
    loadingItems: boolean,
}

function getPhotoGalleryCards(cards: Array<IDashboardCard>): Array<IDashboardCard> {
    return cards.filter(
        (card) => card.dashboard === 'newsroom' && card.type === '4-photo-gallery'
    );
}

export class DashboardPanels extends React.Component<IProps, IState> {
    constructor(props: IProps) {
        super(props);

        const photoGalleryCards = getPhotoGalleryCards(this.props.cards);

        this.state = {
            loadingItems: this.props.fetchCardItems != null || photoGalleryCards.length > 0
        };
    }

    componentDidMount() {
        const photoGalleryCards = getPhotoGalleryCards(this.props.cards);

        if (this.props.fetchCardItems != null || photoGalleryCards.length > 0) {
            // Load items for cards
            Promise.all([
                this.props.fetchCardItems == null ? Promise.resolve() : this.props.fetchCardItems(),
                ...photoGalleryCards.map((card) => (
                    this.props.fetchCardExternalItems(card._id, card.label)
                )),
            ])
                .then(() => {
                    this.setState({loadingItems: false});
                });
        }
    }

    getPanels(card: IDashboardCard) {
        if (this.state.loadingItems) {
            return (
                <CardRow
                    key={card.label}
                    title={card.label}
                    id={card.config.product}
                    isActive={this.props.activeCard === card._id}
                >
                    <div className="col-sm-6 col-md-4 col-lg-3 col-xxl-2 d-flex mb-4">
                        <div className="spinner-border text-success"/>
                        <span className="a11y-only">{gettext('Loading Card Items')}</span>
                    </div>
                </CardRow>
            );
        }

        const Card = getCard(card.type);
        const items = this.props.itemsByCard[card.label] || [];

        if (Card == null) {
            return null;
        } else if (Card._id === '4-photo-gallery') {
            return (
                <Card.dashboardComponent
                    key={card.label}
                    photos={items}
                    title={card.label}
                    moreUrl={card.config.more_url || ''}
                    moreUrlLabel={card.config.more_url_label || ''}
                    listConfig={this.props.listConfig}
                    onMoreNewsClicked={this.props.onMoreNewsClicked}
                />
            );
        } else if (Card._id === '2x2-events') {
            return (
                <Card.dashboardComponent
                    key={card.label}
                    events={card.config.events}
                    title={card.label}
                />
            );
        } else if (Card._id === '6-navigation-row') {
            return (
                <Card.dashboardComponent
                    key={card.label}
                    card={card}
                />
            );
        }

        return Card.dashboardComponent == null ? null : (
            <Card.dashboardComponent
                key={card.label}
                type={card.type}
                items={items}
                title={card.label}
                id={card.config.product}
                openItem={this.props.openItem}
                isActive={this.props.activeCard === card._id}
                cardId={card._id}
                listConfig={this.props.listConfig}
                onMoreNewsClicked={this.props.onMoreNewsClicked}
            />
        );
    }

    render() {
        return this.props.cards.length === 0 ?
            (
                <div className="alert alert-warning my-4" role="alert">
                    <strong>{gettext('Warning')}!</strong>
                    {gettext('There\'s no card defined for {{home}} page!', window.sectionNames)}
                </div>
            ) :
            this.props.cards.map((card) => this.getPanels(card));
    }
}
