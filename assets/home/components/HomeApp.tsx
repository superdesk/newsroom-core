import React from 'react';
import {connect} from 'react-redux';
import {gettext, isDisplayed, isMobilePhone} from 'utils';
import {get} from 'lodash';
import {getCardDashboardComponent} from 'components/cards/utils';
import getItemActions from 'wire/item-actions';
import ItemDetails from 'wire/components/ItemDetails';
import {openItemDetails, setActive, fetchCardExternalItems, fetchCompanyCardItems} from '../actions';
import ShareItemModal from 'components/ShareItemModal';
import DownloadItemsModal from 'wire/components/DownloadItemsModal';
import WirePreview from 'wire/components/WirePreview';
import {followStory} from 'search/actions';
import {downloadMedia} from 'wire/actions';
import {SearchBar} from './search-bar';
import {previewConfigSelector, listConfigSelector, detailsConfigSelector, isSearchEnabled} from 'ui/selectors';
import {filterGroupsToLabelMap} from 'search/selectors';
import CardRow from 'components/cards/render/CardRow';
import {IPersonalizedDashboard, ITopic, PersonalizeHomeSettingsModal} from 'components/PersonalizeHomeModal';
import {personalizeHome} from 'agenda/actions';
import {RadioButtonGroup} from 'features/sections/SectionSwitch';

const modals: any = {
    shareItem: ShareItemModal,
    downloadItems: DownloadItemsModal,
    personalizeHome: PersonalizeHomeSettingsModal,
};

interface IState {
    loadingItems: boolean;
    activeOptionId: string;
}

interface IProps {
    cards: Array<any>;
    itemsByCard: any;
    products: Array<any>;
    user: string;
    userType: string;
    company: string;
    format: Array<any>;
    itemToOpen: any;
    modal: any;
    openItemDetails: () => void;
    activeCard: string;
    actions: Array<{name: string; action: (action?: any) => void;}>;
    fetchCardExternalItems: (cardId: string, cardLabel: string) => void;
    personalizeHome: () => void;
    fetchCompanyCardItems: () => void;
    followStory: () => void;
    previewConfig: any;
    listConfig: any;
    detailsConfig: any;
    downloadMedia: () => void;
    topics: Array<ITopic>;
    isFollowing: boolean;
    isSearchEnabled: boolean;
    filterGroupLabels: any;
}

class HomeApp extends React.Component<IProps, IState> {
    static propTypes: any;

    height: number;
    elem: any;
    constructor(props: any, context: any) {
        super(props, context);
        this.getPanels = this.getPanels.bind(this);
        this.filterActions = this.filterActions.bind(this);
        this.renderModal = this.renderModal.bind(this);
        this.onHomeScroll = this.onHomeScroll.bind(this);
        this.height = 0;

        this.state = {
            loadingItems: true,
            activeOptionId: 'default',
        };
    }

    componentDidMount() {
        (document.getElementById('footer') as any).className = 'footer footer--home';
        this.height = this.elem.offsetHeight;

        // Load items for cards
        Promise.all([
            this.props.fetchCompanyCardItems(),
            ...this.props.cards
                .filter((card: any) => card.dashboard === 'newsroom' && card.type === '4-photo-gallery')
                .map((card: any) => (
                    this.props.fetchCardExternalItems(get(card, '_id'), get(card, 'label'))
                )),
        ])
            .then(() => {
                this.setState({loadingItems: false});
            });
    }

    renderModal(specs: any) {
        if (specs) {
            const Modal = modals[specs.modal];
            return (
                <Modal key="modal" data={specs.data} />
            );
        }
    }

    onHomeScroll(event: any) {
        const container = event.target;
        const BUFFER = 100;
        if(container.scrollTop + this.height + BUFFER >= container.scrollHeight) {
            (document.getElementById('footer') as any).className = 'footer';
        } else {
            (document.getElementById('footer') as any).className = 'footer footer--home';
        }
    }

    getProductId(card: any) {
        return card.config.product;
    }

    getPanelsForPersonalizedDashboard(card: any) {
        const personalizedDashboardTopics = localStorage.getItem('personal-dashboard');
        const homePersonalizedDashboard: IPersonalizedDashboard = personalizedDashboardTopics != null
            ? JSON.parse(personalizedDashboardTopics).find(({name}: IPersonalizedDashboard) => name === 'My Home')
            : null;

        const savedTopicsForPersonalizedDashboard: Array<ITopic> =
            this.props.topics.filter(({_id}) => homePersonalizedDashboard.topicIds.includes(_id));

        const Panel: React.ComponentType<any> = getCardDashboardComponent('4-media-gallery');
        const rawItems: Array<any> = this.props.itemsByCard[card.label] ?? [];
        const topicQueries = savedTopicsForPersonalizedDashboard.map(({query}) => query);

        const groupedItemsByTopic: Dictionary<Array<ITopic>> = topicQueries.reduce((acc, _, i) => {
            const topicQuery = topicQueries?.[i];

            if (topicQuery) {
                const matchedItem = rawItems.filter((x) => x.body_html.toLowerCase().includes(topicQuery));

                return {
                    ...acc,
                    [topicQuery]: matchedItem,
                };
            }

            return acc;
        }, {});

        if (this.state.loadingItems) {
            return (
                <CardRow
                    key={card.label}
                    title={card.label}
                    productId={this.getProductId(card)}
                    isActive={this.props.activeCard === card._id}
                >
                    <div className='col-sm-6 col-md-4 col-lg-3 col-xxl-2 d-flex mb-4'>
                        <div className="spinner-border text-success" />
                        <span className="a11y-only">{gettext('Loading Card Items')}</span>
                    </div>
                </CardRow>
            );
        }

        const gropedItemsTuple = Object.entries(groupedItemsByTopic);

        return (
            !(gropedItemsTuple[0][1].length > 0) ? (
                <div style={{margin: 12}} className="alert alert-warning" role="alert">
                    <strong>{gettext('Warning')}! </strong>
                    {gettext('There\'s no items in these topics!', window.sectionNames)}
                </div>
            ) : (
                gropedItemsTuple.map(([key, items]) => {
                    if (items.length > 0) {
                        return (
                            <Panel
                                key={key}
                                type="4-picture-text"
                                items={items}
                                title={key}
                                productId={this.getProductId(card)}
                                openItem={this.props.openItemDetails}
                                isActive={this.props.activeCard === card._id}
                                cardId={card._id}
                                listConfig={this.props.listConfig}
                            />
                        );
                    }
                })
            )
        );
    }

    getPanels(card: any) {
        if (this.state.loadingItems) {
            return (
                <CardRow key={card.label} title={card.label} productId={this.getProductId(card)} isActive={this.props.activeCard === card._id}>
                    <div className='col-sm-6 col-md-4 col-lg-3 col-xxl-2 d-flex mb-4'>
                        <div className="spinner-border text-success" />
                        <span className="a11y-only">{gettext('Loading Card Items')}</span>
                    </div>
                </CardRow>
            );
        }

        const Panel: React.ComponentType<any> = getCardDashboardComponent(card.type);
        const items = this.props.itemsByCard[card.label] || [];

        if (card.type === '4-photo-gallery') {
            return <Panel
                key={card.label}
                photos={items}
                title={card.label}
                moreUrl={card.config.more_url}
                moreUrlLabel={card.config.more_url_label}
                listConfig={this.props.listConfig}
            />;
        }
        if (card.type === '2x2-events') {
            return <Panel
                key={card.label}
                events={get(card, 'config.events')}
                title={card.label}
                listConfig={this.props.listConfig}
            />;
        }

        return <Panel
            key={card.label}
            type={card.type}
            items={items}
            title={card.label}
            productId={this.getProductId(card)}
            openItem={this.props.openItemDetails}
            isActive={this.props.activeCard === card._id}
            cardId={card._id}
            listConfig={this.props.listConfig}
        />;
    }

    filterActions(item: any, config: any) {
        return this.props.actions.filter((action: any) =>  (!config || isDisplayed(action.id, config)) &&
          (!action.when || action.when(this.props, item)));
    }

    renderContent(children?: any): any {
        const {cards} = this.props;

        return (
            <React.Fragment>
                {this.props.isSearchEnabled && (
                    <SearchBar />
                )}

                <section
                    className="content-main d-block py-4 px-2 p-md-3 p-lg-4"
                    onScroll={this.onHomeScroll}
                    ref={(elem: any) => this.elem = elem}
                >
                    <div className="container-fluid">
                        <div
                            style={{
                                display: 'flex',
                                flexDirection: 'column',
                                alignItems: 'center',
                                gap: 8,
                            }}
                        >
                            <div className="home-tools">
                                <button
                                    onClick={() => {
                                        this.props.personalizeHome();
                                    }}
                                    type="button"
                                    className="nh-button nh-button--secondary nh-button--small"
                                    title="Personalize Home"
                                >
                                    Personalize Home
                                </button>
                            </div>
                            {/*
                                TODO: The next block should only appear if
                                there already is personal home/dashboard
                            */}
                            <div>
                                <div
                                    style={{
                                        display: 'flex',
                                        flexDirection: 'row',
                                        alignItems: 'center'
                                    }}
                                    className="home-tools"
                                >
                                    <RadioButtonGroup
                                        options={[
                                            {
                                                _id: 'default',
                                                name: 'Default'
                                            },
                                            {
                                                _id: 'my-home',
                                                name: 'My home'
                                            }
                                        ]}
                                        activeOptionId={this.state.activeOptionId}
                                        switchOptions={(optionId) => {
                                            this.setState({
                                                activeOptionId: optionId
                                            });
                                        }}
                                    />
                                    <button
                                        onClick={() => {
                                            this.props.personalizeHome();
                                        }}
                                        type="button"
                                        className="icon-button icon-button--small icon-button--tertiary icon-button--bordered"
                                        title="Edit personal Home"
                                    >
                                        <i className="icon--settings"></i>
                                    </button>
                                </div>
                            </div>
                        </div>
                        {this.props.modal?.modal === 'personalizeHome' && <PersonalizeHomeSettingsModal />}
                        {
                            this.state.activeOptionId != 'my-home' && cards.length > 0
                                ? (
                                    this.props.cards
                                        .filter((c: any) => c.dashboard === 'newsroom')
                                        .map((card: any) => this.getPanels(card))
                                )
                                : cards.length > 0 && this.getPanelsForPersonalizedDashboard(this.props.cards[0])
                        }
                        {
                            cards.length === 0 && (
                                <div className="alert alert-warning" role="alert">
                                    <strong>{gettext('Warning')}!</strong>
                                    {gettext('There\'s no card defined for {{home}} page!', window.sectionNames)}
                                </div>
                            )
                        }
                    </div>
                    {children}
                </section>
            </React.Fragment>
        );
    }

    renderNonMobile() {
        const modal = this.renderModal(this.props.modal);

        return (
            (
                this.props.itemToOpen ? [
                    <ItemDetails key="itemDetails"
                        item={this.props.itemToOpen}
                        user={this.props.user}
                        topics={this.props.topics}
                        actions={this.filterActions(this.props.itemToOpen, this.props.previewConfig)}
                        onClose={() => this.props.actions.filter((a: any) => a.id === 'open')[0].action(null)}
                        followStory={this.props.followStory}
                        detailsConfig={this.props.detailsConfig}
                        filterGroupLabels={this.props.filterGroupLabels}
                        downloadMedia={this.props.downloadMedia}
                    />,
                    modal
                ] : this.renderContent()
            )
        );
    }

    renderMobile() {
        const modal = this.renderModal(this.props.modal);
        const isFollowing = get(this.props, 'itemToOpen.slugline') && this.props.topics &&
            this.props.topics.find((topic: any) => topic.query === `slugline:"${this.props.itemToOpen.slugline}"`);

        return this.renderContent([
            <div key='preview_test' className={`wire-column__preview ${this.props.itemToOpen ? 'wire-column__preview--open' : ''}`}>
                {this.props.itemToOpen && (
                    <WirePreview
                        item={this.props.itemToOpen}
                        user={this.props.user}
                        actions={this.filterActions(this.props.itemToOpen, this.props.previewConfig)}
                        followStory={this.props.followStory}
                        isFollowing={!!isFollowing}
                        closePreview={() => this.props.actions.filter((a: any) => a.id === 'open')[0].action(null)}
                        previewConfig={this.props.previewConfig}
                        downloadMedia={this.props.downloadMedia}
                        listConfig={this.props.listConfig}
                        filterGroupLabels={this.props.filterGroupLabels}
                    />
                )}
            </div>,
            modal
        ]);
    }

    render() {
        return isMobilePhone() ?
            this.renderMobile() :
            this.renderNonMobile();
    }
}

const mapStateToProps = (state: any) =>({
    cards: state.cards,
    itemsByCard: state.itemsByCard,
    products: state.products,
    user: state.user,
    userType: state.userType,
    company: state.company,
    itemToOpen: state.itemToOpen,
    modal: state.modal,
    activeCard: state.activeCard,
    previewConfig: previewConfigSelector(state),
    listConfig: listConfigSelector(state),
    detailsConfig: detailsConfigSelector(state),
    topics: state.topics || [],
    isSearchEnabled: isSearchEnabled(state),
    filterGroupLabels: filterGroupsToLabelMap(state),
});

const mapDispatchToProps = (dispatch: any, state: any) => ({
    openItemDetails: (item: any, cardId: any) => {
        dispatch(openItemDetails(item));
        dispatch(setActive(cardId));
    },
    personalizeHome: () => {
        dispatch(personalizeHome());
    },
    actions: getItemActions(dispatch),
    fetchCardExternalItems: (cardId: any, cardLabel: any) => dispatch(fetchCardExternalItems(cardId, cardLabel)),
    fetchCompanyCardItems: () => dispatch(fetchCompanyCardItems()),
    followStory: (item: any) => followStory(item, 'wire'),
    downloadMedia: (href: any, id: any) => dispatch(downloadMedia(href, id)),
});


export default connect(mapStateToProps, mapDispatchToProps)(HomeApp);
