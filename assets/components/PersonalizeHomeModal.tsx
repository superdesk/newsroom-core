/* eslint-disable react/no-unescaped-entities */
import React from 'react';
import {connect} from 'react-redux';
import {partition} from 'lodash';
import {gettext} from 'utils';
import Modal from 'components/Modal';
import {Input} from 'reactstrap';
import CheckboxInput from './CheckboxInput';
import {IUser, IUserDashboard} from 'interfaces/user';
import {RadioButtonGroup} from 'features/sections/SectionSwitch';
import {modalFormInvalid, modalFormValid} from 'actions';
import {updateUser} from 'users/actions';
import {getCurrentUser} from 'company-admin/selectors';
import {IAgendaState} from 'agenda/reducers';
import {ITopic} from 'interfaces/topic';
import {IPersonalizedDashboardsWithData} from 'home/reducers';

interface IMapStateProps {
    topics: Array<ITopic>;
    currentUser: IUser;
}

interface IMapDispatchProps {
    saveUser: (updates: Partial<IUser>) => void;
    modalFormValid: () => void;
    modalFormInvalid: () => void;
}

interface IOwnProps {
    personalizedDashboards: Array<IPersonalizedDashboardsWithData>;
    closeModal?: () => void;
}

type IProps = IMapStateProps & IMapDispatchProps & IOwnProps;

interface IState {
    selectedTopicIds: Array<string>;
    activeSection: string;
    searchTerm: string;
    isLoading: boolean;
}

const MAX_SELECTED_TOPICS = 6;

class PersonalizeHomeModal extends React.Component<IProps, IState> {

    wireTopics: Array<ITopic>;
    wireTopicsById: Map<ITopic['_id'], ITopic>;

    constructor(props: any) {
        super(props);

        const [wireTopics, agendaTopics] = partition(this.props.topics, (topic) => topic.topic_type === 'wire');

        this.wireTopics = wireTopics ?? [];
        this.wireTopicsById = new Map(this.wireTopics.map((topic) => [topic._id, topic]));

        this.state = {
            selectedTopicIds: (this.props.personalizedDashboards?.[0]?.topic_items ?? []).map((item) => item._id),
            activeSection: '1',
            searchTerm: '',
            isLoading: false,
        };
    }

    componentDidUpdate(): void {
        if (this.state.selectedTopicIds.length > 0) {
            this.props.modalFormValid();
        } else {
            this.props.modalFormInvalid();
        }
    }

    handleChange(topicId: string) {
        let updatedTopics = this.state.selectedTopicIds.concat();

        if (this.state.selectedTopicIds.includes(topicId)) {
            updatedTopics = updatedTopics.filter((_id) => _id !== topicId);
        } else if (this.state.selectedTopicIds.length < MAX_SELECTED_TOPICS) {
            updatedTopics.unshift(topicId);
        }

        this.setState({
            selectedTopicIds: updatedTopics,
        });
    }

    addCustomDashboard(name: string) {
        this.setState({isLoading: true});

        const newDashboard: IUserDashboard = {
            type: '4-picture-text',
            topic_ids: this.state.selectedTopicIds,
            name: name,
        };

        this.props.saveUser({dashboards: [newDashboard]});

        this.setState({isLoading: false});
    }

    getSelectedTopics() {
        const topics: Array<ITopic> = [];

        this.state.selectedTopicIds.map((topicId) => this.wireTopicsById.get(topicId)).forEach((topic) => {
            if (topic != null) {
                topics.push(topic);
            }
        });

        return topics;
    }

    render() {
        const NoSearchMatches = () => (
            <div className="empty-state__container mt-3">
                <div className="empty-state empty-state--small">
                    <figure className="empty-state__graphic">
                        <img src="/static/empty-states/empty_state--small.svg" role="presentation" alt="" />
                    </figure>
                    <figcaption className="empty-state__text">
                        <h4 className="empty-state__text-heading">{gettext('You don\'t have any saved Topics yet.')}</h4>
                        <p className="empty-state__text-description">
                            {gettext('You can create Topics by saving search terms and/or filters from the Wire section.')}
                        </p>
                        <div className="empty-state__links">
                            <a className="" href="/wire">{gettext('Go to Wire')}</a>
                        </div>
                    </figcaption>
                </div>
            </div>
        );

        const NoSelectedTopics = () => (
            <div className="empty-state__container empty-state__container--full-height">
                <div
                    style={{
                        display: 'flex',
                        flexDirection: 'column',
                        alignItems: 'center',
                    }}
                    className="empty-state empty-state--large"
                >
                    <figure className="empty-state__graphic">
                        <img src="/static/empty-states/empty_state--large.svg" role="presentation" alt="" />
                    </figure>
                    <figcaption className="empty-state__text">
                        <h4 className="empty-state__text-heading">{gettext('No items yet')}</h4>
                        <p className="empty-state__text-description">
                            {gettext('Select some topics from the sidebar to add them here.')}
                        </p>
                    </figcaption>
                </div>
            </div>
        );

        const filteredTopics = (topics: Array<ITopic>) =>
            topics.filter(({is_global}) => this.state.activeSection === '1' ? is_global != true : is_global === true);

        const searchMatches = filteredTopics(this.wireTopics)
            .filter((topic) => topic.label.toLowerCase().includes(this.state.searchTerm.toLowerCase()))
            .map((topic) => (
                <CheckboxInput
                    key={topic._id}
                    value={this.state.selectedTopicIds.includes(topic._id)}
                    onChange={() => {
                        this.handleChange(topic._id);
                    }}
                    label={gettext(topic.label)}
                />
            ));

        const topicSearch = (searchMatches?.length ?? 0) > 0
            ? (
                <div style={{padding: 4}}>
                    {searchMatches}
                </div>
            ) : <NoSearchMatches />;

        const groupedTopics = (this.props.topics?.length ?? 0) > 0 ? (
            <div>
                <div className='boxed-checklist'>
                    {filteredTopics(this.wireTopics).map((wireTopic) => (
                        <CheckboxInput
                            key={wireTopic._id}
                            value={this.state.selectedTopicIds.includes(wireTopic._id)}
                            onChange={() => {
                                this.handleChange(wireTopic._id);
                            }}
                            label={gettext(wireTopic.label)}
                        />
                    ))}
                </div>
            </div>
        ) : (
            NoSearchMatches()
        );

        const selectedTopics = (
            <div className="simple-card__list pt-3">
                {this.getSelectedTopics().map((topic) => {
                    return (
                        <div
                            key={topic._id}
                            className="simple-card flex-row simple-card--compact" // class simple-card--draggable is removed because drag and drop isn't implemented yet
                        >
                            <div className='simple-card__content'>
                                <h6 className="simple-card__headline" title="">{topic.label}</h6>
                                <div className="simple-card__row">
                                    <div className="simple-card__column simple-card__column--align-start">
                                        <span className="simple-card__date">
                                            {topic.is_global != false ? gettext('Company Topics') : gettext('My Topics')}
                                        </span>
                                    </div>
                                </div>
                            </div>
                            <div className='simple-card__actions'>
                                <button
                                    type="button"
                                    className="icon-button icon-button--secondary icon-button--small"
                                    title=""
                                    aria-label={gettext('Delete')}
                                    onClick={() => {
                                        this.handleChange(topic._id);
                                    }}
                                >
                                    <i className="icon--trash" />
                                </button>
                            </div>
                        </div>
                    );
                })}
            </div>
        );

        return (
            <Modal
                width="full"
                closeModal={this.props.closeModal}
                title={gettext('Personalize Home')}
                onSubmitLabel={gettext('Save')}
                disableButtonOnSubmit={this.state.isLoading}
                onSubmit={() => {
                    this.addCustomDashboard(gettext('My Home'));
                }}
            >
                <div
                    className="full-page-layout__content"
                    style={{
                        height: '100%',
                    }}
                >
                    <aside className="full-page-layout__content-aside">
                        <div className="full-page-layout__content-aside-inner">
                            <p className='font-size--medium text-color--muted mt-1 mb-3'>
                                {gettext('Select up to 6 Topics you want to display on your personal Home screen.')}
                            </p>
                            <p className='font-size--large'>
                                {
                                    gettext(
                                        '{{size}} out of 6 topics selected',
                                        {size: this.state.selectedTopicIds.length}
                                    )
                                }
                            </p>
                            <RadioButtonGroup
                                activeOptionId={this.state.activeSection}
                                size='small'
                                fullWidth
                                className='mb-3'
                                options={[
                                    {
                                        _id: '1',
                                        name: gettext('My Topics'),
                                    },
                                    {
                                        _id: '2',
                                        name: gettext('Company Topics'),
                                    },
                                ]}
                                switchOptions={(optionId) => {
                                    this.setState({
                                        activeSection: optionId
                                    });
                                }}
                            />
                            <div className="search search--small search--with-icon search--bordered m-0">
                                <form className="search__form" role="search" aria-label="search">
                                    <i className="icon--search icon--muted-2"></i>
                                    <input
                                        onChange={(e) => {
                                            this.setState({
                                                searchTerm: e.target.value,
                                            });
                                        }}
                                        value={this.state.searchTerm}
                                        type="text"
                                        name="q"
                                        className="search__input form-control"
                                        placeholder={gettext('Search Topics')}
                                        aria-label={gettext('Search Topics')}
                                    />
                                    <div className="search__form-buttons">
                                        <button className="search__button-clear" aria-label={gettext('Clear search')} type="reset">
                                            <svg fill="none" height="18" viewBox="0 0 18 18" width="18" xmlns="http://www.w3.org/2000/svg">
                                                <path clipRule="evenodd" d="m9 18c4.9706 0 9-4.0294 9-9 0-4.97056-4.0294-9-9-9-4.97056 0-9 4.02944-9 9 0 4.9706 4.02944 9 9 9zm4.9884-12.58679-3.571 3.57514 3.5826 3.58675-1.4126 1.4143-3.58252-3.5868-3.59233 3.5965-1.41255-1.4142 3.59234-3.59655-3.54174-3.54592 1.41254-1.41422 3.54174 3.54593 3.57092-3.57515z" fill="var(--color-text)" fillRule="evenodd" opacity="1"></path>
                                            </svg>
                                        </button>
                                    </div>
                                </form>
                            </div>
                            {this.state.searchTerm ? topicSearch : groupedTopics}
                        </div>
                    </aside>
                    <div
                        className='full-page-layout__content-main'
                    >
                        <Input disabled value={gettext('My Home')} />
                        {/* FIXME: For the MVP we won't have the option for draggable list items sorting */}
                        {/* <div className="py-3 mt-4 mb-2 border border--medium border-start-0 border-end-0 border--dotted">
                            <p className='font-size--medium text-color--muted m-0'>
                                <span className='text-color--default fw-bold'>Hint: </span>
                                Drag and drop items to change the order. This will change the order of the topics are displayed on the Home screen.
                            </p>
                        </div> */}
                        {this.state.selectedTopicIds.length > 0 ? selectedTopics : <NoSelectedTopics />}
                    </div>
                </div>
            </Modal>
        );
    }
}

const mapStateToProps = (state: IAgendaState) => ({
    topics: state.topics,
    currentUser: getCurrentUser(state),
});

const mapDispatchToProps = ({
    modalFormValid: () => modalFormValid(),
    modalFormInvalid: () => modalFormInvalid(),
    saveUser: (updates: Partial<IUser>) => updateUser(updates),
});

export const PersonalizeHomeSettingsModal =
    connect<IMapStateProps, IMapDispatchProps, IOwnProps, IAgendaState>(mapStateToProps, mapDispatchToProps)(PersonalizeHomeModal);
