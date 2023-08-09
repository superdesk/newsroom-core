/* eslint-disable react/no-unescaped-entities */
import React from 'react';
import {connect} from 'react-redux';
import {partition} from 'lodash';
import {gettext} from 'utils';
import Modal from 'components/Modal';
import {Input} from 'reactstrap';
import CheckboxInput from './CheckboxInput';
import {reloadMyTopics as reloadMyWireTopics} from 'wire/actions';
import {IUser, IUserDashboard} from 'interfaces/user';
import {RadioButtonGroup} from 'features/sections/SectionSwitch';
import {modalFormInvalid, modalFormValid} from 'actions';
import {updateUser} from 'users/actions';
import {getCurrentUser} from 'company-admin/selectors';
import {IAgendaState} from 'agenda/reducers';
import {ITopic} from 'interfaces/topic';

interface IStateProps {
    topics: Array<ITopic>;
    currentUser: IUser;
}

interface IDispatchProps {
    saveUser: (updates: Partial<IUser>) => void;
    modalFormValid: () => void;
    modalFormInvalid: () => void;
}

interface IOwnProps {
    closeModal?: () => void;
}

type IProps = IStateProps & IDispatchProps & IOwnProps;

interface IState {
    selectedTopics: Array<string>;
    activeSection: string;
    searchTerm: string;
    isLoading: boolean;
}

const MAX_SELECTED_TOPICS = 6;

const getSelectedTopics = (user: IUser) => {
    if (user.dashboards?.length) {
        return user.dashboards[0].topic_ids || [];
    }

    return [];
};

class PersonalizeHomeModal extends React.Component<IProps, IState> {
    constructor(props: any) {
        super(props);

        this.state = {
            selectedTopics: getSelectedTopics(this.props.currentUser),
            activeSection: '1',
            searchTerm: '',
            isLoading: false,
        };
    }

    componentDidUpdate(): void {
        if (this.state.selectedTopics.length > 0) {
            this.props.modalFormValid();
        } else {
            this.props.modalFormInvalid();
        }
    }

    handleChange(topicId: string) {
        let updatedTopics = this.state.selectedTopics.concat();

        if (this.state.selectedTopics.includes(topicId)) {
            updatedTopics = updatedTopics.filter((_id) => _id !== topicId);
        } else if (this.state.selectedTopics.length < MAX_SELECTED_TOPICS) {
            updatedTopics.unshift(topicId);
        }

        this.setState({
            selectedTopics: updatedTopics
        });
    }

    addCustomDashboard(name: string) {
        this.setState({isLoading: true});

        const newDashboard: IUserDashboard = {
            type: '4-picture-text',
            topic_ids: this.state.selectedTopics,
            name: name,
        };

        this.props.saveUser({dashboards: [newDashboard]});

        this.setState({isLoading: false});
    }

    render() {
        const [wireTopics, agendaTopics] = partition(this.props.topics, (topic) => topic.topic_type === 'wire');

        const NoSearchMatches = () => (
            <div className="empty-state__container mt-3">
                <div className="empty-state">
                    <figure className="empty-state__graphic">
                        <img src="/static/empty-states/empty_state--small.svg" role="presentation" alt="" />
                    </figure>
                    <figcaption className="empty-state__text">
                        <h4 className="empty-state__text-heading">{gettext('You don\'t have any saved Topics yet.')}</h4>
                        <p className="empty-state__text-description">
                            {gettext('You can create Topics by saving search terms and/or filters from the Wire and Agenda sections.')}
                        </p>
                        <div className="empty-state__links">
                            <a className="" href="/wire">{gettext('Go to Wire')}</a>
                            <a className="" href="/agenda">{gettext('Go to Agenda')}</a>
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
                        <img src="/static/empty-states/empty_state--small.svg" role="presentation" alt="" />
                    </figure>
                    <figcaption className="empty-state__text">
                        <h4 className="empty-state__text-heading">{gettext('You don\'t have any saved Topics yet')}</h4>
                        <p className="empty-state__text-description">
                            {gettext('You can create Topics by saving search terms and/or filters from the Wire and Agenda sections.')}
                        </p>
                    </figcaption>
                </div>
            </div>
        );

        const filteredTopics = (topics: Array<ITopic>) =>
            topics.filter(({is_global}) => this.state.activeSection === '1' ? is_global != true : is_global === true);

        const searchMatches = filteredTopics(wireTopics ?? [])
            .filter((topic) => topic.label.toLowerCase().includes(this.state.searchTerm.toLowerCase()))
            .map((topic) => (
                <CheckboxInput
                    key={topic._id}
                    value={this.state.selectedTopics.includes(topic._id)}
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
                    {filteredTopics(wireTopics).map((wireTopic) => (
                        <CheckboxInput
                            key={wireTopic._id}
                            value={this.state.selectedTopics.includes(wireTopic._id)}
                            onChange={() => {
                                this.handleChange(wireTopic._id);
                            }}
                            label={gettext(wireTopic.label)}
                        />
                    ))}
                </div>
                {/* <FormToggle
                    expanded={true}
                    title={gettext('Agenda topics')}
                    testId="toggle--general"
                >
                    {
                        filteredTopics(agendaTopics).map((agendaTopic) => (
                            <CheckboxInput
                                key={agendaTopic._id}
                                value={this.state.selectedTopics.has(agendaTopic._id)}
                                onChange={() => {
                                    this.handleChange(agendaTopic._id);
                                }}
                                label={gettext(agendaTopic.label)}
                            />
                        ))
                    }
                </FormToggle> */}
            </div>
        ) : (
            NoSearchMatches()
        );

        const selectedTopics = (
            <div className="simple-card__list pt-3">
                {this.state.selectedTopics.map((topicId: string) => wireTopics.find((topic) => topic._id === topicId)).map((topic) => {
                    if (topic == null) {
                        return null;
                    }

                    return (
                        <div
                            style={{
                                width: '100%',
                            }}
                            key={topic._id}
                            className="simple-card flex-row simple-card--compact simple-card--draggable"
                        >
                            <div style={{paddingLeft: 24}} className='simple-card__content'>
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
                    style={{
                        display: 'flex',
                        flexDirection: 'row',
                        justifyContent: 'space-between',
                        gap: 12,
                        height: '100%',
                    }}
                >
                    <aside style={{width: '25%'}} className="full-page-layout__content-aside">
                        <div className="full-page-layout__content-aside-inner">
                            <p className='font-size--medium text-color--muted mt-1 mb-3'>
                                {gettext('Select up to 6 Topics you want to display on your personal Home screen.')}
                            </p>
                            <p className='font-size--large'>{gettext('{{size}} out of 6 topics selected', {size: this.state.selectedTopics.length || 0})}</p>
                            <RadioButtonGroup
                                activeOptionId={this.state.activeSection}
                                options={[
                                    {
                                        _id: '1',
                                        name: gettext('My topics'),
                                    },
                                    {
                                        _id: '2',
                                        name: gettext('Company topics'),
                                    },
                                ]}
                                switchOptions={(optionId) => {
                                    this.setState({
                                        activeSection: optionId
                                    });
                                }}
                            />
                            <div style={{padding: 6}} />
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
                        style={{
                            width: '75%',
                            display: 'flex',
                            flexDirection: 'column',
                            alignItems: 'center',
                        }}
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
                        {this.state.selectedTopics.length > 0 ? selectedTopics : <NoSelectedTopics />}
                    </div>
                </div>
            </Modal>
        );
    }
}

const mapStateToProps = (state: IAgendaState) : IStateProps => ({
    topics: state.topics,
    currentUser: getCurrentUser(state),
});

const mapDispatchToProps = ({
    modalFormValid: () => modalFormValid(),
    modalFormInvalid: () => modalFormInvalid(),
    saveUser: (updates: Partial<IUser>) => updateUser(updates),
});

export const PersonalizeHomeSettingsModal =
    connect<IStateProps, IDispatchProps, IOwnProps, IAgendaState>(mapStateToProps, mapDispatchToProps)(PersonalizeHomeModal);
