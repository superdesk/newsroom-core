import React from 'react';
import {connect} from 'react-redux';
import {get} from 'lodash';

import {ITopic, IItemAction} from 'interfaces';
import {gettext, isDisplayed, isMobilePhone} from 'utils';
import {getCard} from 'components/cards/utils';
import getItemActions from 'wire/item-actions';
import ItemDetails from 'wire/components/ItemDetails';
import {openItemDetails, setActive, fetchCardExternalItems, fetchCompanyCardItems} from '../actions';
import ShareItemModal from 'components/ShareItemModal';
import DownloadItemsModal from 'wire/components/DownloadItemsModal';
import WirePreview from 'wire/components/WirePreview';
import {followStory} from 'search/actions';
import {downloadMedia, fetchItems} from 'wire/actions';
import {SearchBar} from './search-bar';
import {previewConfigSelector, listConfigSelector, detailsConfigSelector, isSearchEnabled} from 'ui/selectors';
import {filterGroupsToLabelMap} from 'search/selectors';
import {PersonalizeHomeSettingsModal} from 'components/PersonalizeHomeModal';
import {personalizeHome} from 'agenda/actions';
import {RadioButtonGroup} from 'features/sections/SectionSwitch';
import {getCurrentUser} from 'company-admin/selectors';
import {IPersonalizedDashboardsWithData} from 'home/reducers';
import {Button} from 'components/Buttons';
import {IconButton} from 'components/IconButton';

import {DashboardPanels} from './DashboardPanels';

export const WIRE_SECTION = 'wire';

const modals: any = {
    shareItem: ShareItemModal,
    downloadItems: DownloadItemsModal,
    personalizeHome: PersonalizeHomeSettingsModal,
};

interface IState {
    activeOptionId: 'default' | 'my-home';
}

interface IStateProps {
    cards: Array<any>;
    personalizedDashboards: Array<IPersonalizedDashboardsWithData>;
    itemsByCard: any;
    products: Array<any>;
    user: string;
    userType: string;
    userSections: any;
    company: string;
    itemToOpen: any;
    modal: any;
    activeCard: string;
    previewConfig: any;
    listConfig: any;
    detailsConfig: any;
    topics: Array<ITopic>;
    isSearchEnabled: boolean;
    filterGroupLabels: any;
    currentUser: any;
}

interface IDispatchProps {
    openItemDetails: (item: any, state: any) => void;
    fetchItems: () => any;
    personalizeHome: () => void;
    actions: Array<IItemAction>;
    fetchCardExternalItems: (cardId: string, cardLabel: string) => any;
    fetchCompanyCardItems: () => any;
    followStory: (item: any) => void;
    downloadMedia: (href: any, id: any) => any;
}

type IProps = IStateProps & IDispatchProps;

class HomeApp extends React.Component<IProps, IState>  {
    static propTypes: any;

    height: number;
    elem: any;
    hasPersonalDashboard: boolean;

    constructor(props: any, context: any) {
        super(props, context);
        this.filterActions = this.filterActions.bind(this);
        this.renderModal = this.renderModal.bind(this);
        this.onHomeScroll = this.onHomeScroll.bind(this);
        this.height = 0;

        this.hasPersonalDashboard = (this.props.personalizedDashboards?.[0]?.topic_items?.length ?? 0) > 0;

        this.state = {
            activeOptionId: this.hasPersonalDashboard ? 'my-home' : 'default',
        };
    }

    componentDidMount() {
        (document.getElementById('footer') as any).className = 'footer footer--home';
        this.height = this.elem.offsetHeight;
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
        if (container.scrollTop + this.height + BUFFER >= container.scrollHeight) {
            (document.getElementById('footer') as any).className = 'footer';
        } else {
            (document.getElementById('footer') as any).className = 'footer footer--home';
        }
    }

    getPanelsForPersonalizedDashboard() {
        const {personalizedDashboards} = this.props;
        const Card = getCard('4-picture-text');
        const personalizedDashboardTopicIds = personalizedDashboards?.[0].topic_items?.map(({_id}) => _id);
        const topicItems = this.props.topics.filter(({_id}) => personalizedDashboardTopicIds?.includes(_id));

        return (
            personalizedDashboards?.[0].topic_items?.map((item) => {
                const currentTopic = topicItems.find(({_id}) => _id === item._id);

                return (
                    Card?._id === '4-picture-text' && currentTopic && (
                        <Card.dashboardComponent
                            kind="topic"
                            key={item._id}
                            type="4-picture-text"
                            items={item.items}
                            title={currentTopic?.label}
                            id={currentTopic?._id}
                            openItem={this.props.openItemDetails}
                            isActive={this.props.activeCard === item._id}
                            cardId={item._id}
                            listConfig={this.props.listConfig}
                        />
                    )
                );
            })
        );
    }

    filterActions(item: any, config: any) {
        return this.props.actions.filter((action: any) => (!config || isDisplayed(action.id, config)) &&
            (!action.when || action.when(this.props, item)));
    }

    renderContent(children?: any): any {
        const isWireSectionConfigured = this.props.userSections[WIRE_SECTION] != null;

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
                        {
                            isWireSectionConfigured && (
                                <div className="home-tools__container">
                                    {
                                        !this.hasPersonalDashboard ? (
                                            <div className="home-tools">
                                                <Button
                                                    value={gettext('Personalize Home')}
                                                    variant='secondary'
                                                    size='small'
                                                    onClick={() => {
                                                        this.props.personalizeHome();
                                                    }}
                                                />
                                            </div>
                                        ) : (
                                            <div className="home-tools">
                                                <RadioButtonGroup
                                                    size='small'
                                                    options={[
                                                        {
                                                            _id: 'default',
                                                            name: gettext('Default')
                                                        },
                                                        {
                                                            _id: 'my-home',
                                                            name: gettext('My Home')
                                                        },
                                                    ]}
                                                    activeOptionId={this.state.activeOptionId}
                                                    switchOptions={(optionId) => {
                                                        if (optionId === 'default' || optionId === 'my-home') {
                                                            this.setState({
                                                                activeOptionId: optionId
                                                            });
                                                        }
                                                    }}
                                                />
                                                <IconButton
                                                    icon='settings'
                                                    variant='tertiary'
                                                    size='small'
                                                    border
                                                    tooltip={gettext('Edit personal Home')}
                                                    ariaLabel={gettext('Edit personal Home')}
                                                    onClick={() => {
                                                        this.props.personalizeHome();
                                                    }}
                                                />
                                            </div>
                                        )
                                    }
                                </div>
                            )
                        }
                        {
                            this.props.modal?.modal === 'personalizeHome' && (
                                <PersonalizeHomeSettingsModal
                                    personalizedDashboards={this.props.personalizedDashboards}
                                />
                            )
                        }
                        {
                            this.state.activeOptionId === 'my-home' ? (
                                this.getPanelsForPersonalizedDashboard()
                            ) : (
                                <DashboardPanels
                                    cards={this.props.cards.filter((card) => card.dashboard === 'newsroom')}
                                    activeCard={this.props.activeCard}
                                    itemsByCard={this.props.itemsByCard}
                                    listConfig={this.props.listConfig}
                                    fetchCardItems={this.props.fetchCompanyCardItems}
                                    fetchCardExternalItems={this.props.fetchCardExternalItems}
                                    openItem={this.props.openItemDetails}
                                />
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
                        onClose={() => this.props.actions.filter((a: any) => a.id === 'open')[0].action()}
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
                        closePreview={() => this.props.actions.filter((a) => a.id === 'open')[0].action()}
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

const mapStateToProps = (state: any) => ({
    cards: state.cards,
    personalizedDashboards: state.personalizedDashboards,
    itemsByCard: state.itemsByCard,
    products: state.products,
    user: state.user,
    userType: state.userType,
    userSections: state.userSections,
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
    currentUser: getCurrentUser(state),
});

const mapDispatchToProps = (dispatch: any, state: any) => ({
    openItemDetails: (item: any, cardId: any) => {
        dispatch(openItemDetails(item));
        dispatch(setActive(cardId));
    },
    fetchItems: () => dispatch(fetchItems()),
    personalizeHome: () => {
        dispatch(personalizeHome());
    },
    actions: getItemActions(dispatch),
    fetchCardExternalItems: (cardId: any, cardLabel: any) => dispatch(fetchCardExternalItems(cardId, cardLabel)),
    fetchCompanyCardItems: () => dispatch(fetchCompanyCardItems()),
    followStory: (item: any) => followStory(item, 'wire'),
    downloadMedia: (href: any, id: any) => dispatch(downloadMedia(href, id)),
});


export default connect<
    IStateProps,
    IDispatchProps,
    {},
    any
>(mapStateToProps, mapDispatchToProps)(HomeApp);
