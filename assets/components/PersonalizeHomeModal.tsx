import React from 'react';
import {connect} from 'react-redux';
import {get, range, partition, isMatch} from 'lodash';
import {gettext} from 'utils';
import Modal from 'components/Modal';
import {Input} from 'reactstrap';
import CheckboxInput from './CheckboxInput';
import {FormToggle} from 'ui/components/FormToggle';
import {reloadMyTopics as reloadMyWireTopics} from 'wire/actions';
import {IUser} from 'interfaces/user';
import {RadioButtonGroup} from 'features/sections/SectionSwitch';

interface IReduxStoreProps {
    itemsById: Array<any>;
    formValid: any;
    topics: Array<any>;
}

interface IProps extends IReduxStoreProps {
    closeModal: () => void;
    submit: any;
    data: any;
}

interface IState {
    checked: boolean;
    checkedTopics: Array<ITopic>;
    allTopics: Array<ITopic>;
    activeSection: string;
    searchTerm: string;
}

type Dictionary = {[key: string]: string};

interface ITopic {
    _id: string;
    label: string;
    query?: string;
    filter?: Dictionary;
    created?: Dictionary;
    user: IUser['_id'];
    company: any;
    is_global?: boolean;
    subscribers: Array<IUser['_id']>;
    timezone_offset?: number;
    topic_type: 'wire' | 'agenda';
    navigation?: Array<string>;
    original_creator: IUser['_id'];
    version_creator: IUser['_id'];
    folder: string;
    advanced?: Dictionary;
}

class PersonalizeHomeModal extends React.Component<IProps, IState> {
    constructor(props: any) {
        super(props);

        this.state = {
            checked: false,
            checkedTopics: [],
            allTopics: [],
            activeSection: '1',
            searchTerm: '',
        };
    }

    // componentDidMount(): void {
    //     server.get('/topics/my_topics').then((topics) => {
    //         this.setState({
    //             allTopics: topics,
    //         });
    //     });
    // }

    handleChange(isIncluded: boolean, topic: ITopic) {
        if (this.state.checkedTopics.length < 6) {
            if (isIncluded) {
                this.setState({
                    checkedTopics: this.state.checkedTopics
                        .filter((topic) => topic._id !== topic._id)
                });
            } else {
                this.setState({
                    checkedTopics: [
                        topic,
                        ...this.state.checkedTopics
                    ],
                });
            }
        }
    }

    isIncluded(topicId: string) {
        return this.state.checkedTopics.map(({_id}) => _id).includes(topicId);
    }

    render() {
        if (this.state.allTopics == null) {
            return (
                <div className="empty-state__container mt-3">
                    <div className="empty-state">
                        <figure className="empty-state__graphic">
                            <img src="/static/empty-states/empty_state--small.svg" role="presentation" alt="" />
                        </figure>
                        <figcaption className="empty-state__text">
                            <h4 className="empty-state__text-heading">You don't have any saved Topics yet</h4>
                            <p className="empty-state__text-description">
                                You can create Topics by saving search terms and/or filters from the Wire and Agenda sections.
                            </p>
                            <div className="empty-state__links">
                                <a className="" href="">Go to Wire</a>
                                <a className="" href="">Go to Agenda</a>
                            </div>
                        </figcaption>
                    </div>
                </div>
            );
        }

        const topicsMocked: Array<ITopic> = range(1, 10).map((x) => {
            return {
                _id: x,
                label: `${x}`,
                user: x,
                company: x,
                subscribers: [x],
                topic_type: x % 2 === 0 ? 'wire' : 'agenda',
                original_creator: x,
                version_creator: x,
                folder: x,
            } as unknown as ITopic;
        });

        const [wireTopics, agendaTopics] = partition(topicsMocked, (topic) => topic.topic_type === 'wire');

        const searchedTopics = topicsMocked.map((topic) => {
            if (isMatch(topic, {label: this.state.searchTerm})) {
                const isIncluded = this.isIncluded(topic._id);

                return (
                    <CheckboxInput
                        key={topic._id}
                        value={isIncluded}
                        onChange={() => {
                            this.handleChange(isIncluded, topic);
                        }}
                        label={gettext(topic.label)}
                    />
                );
            }

            return null;
        });

        const groupedTopics = (topicsMocked?.length ?? 0) > 0 ? (
            <div>
                <FormToggle
                    expanded={true}
                    title={gettext('Wire topics')}
                    testId="toggle--general"
                >
                    {
                        wireTopics.map((wireTopic) => {
                            const isIncluded = this.isIncluded(wireTopic._id);

                            return (
                                <CheckboxInput
                                    key={wireTopic._id}
                                    value={isIncluded}
                                    onChange={() => {
                                        this.handleChange(isIncluded, wireTopic);
                                    }}
                                    label={gettext(wireTopic.label)}
                                />
                            );
                        })
                    }
                </FormToggle>
                <FormToggle
                    expanded={true}
                    title={gettext('Agenda topics')}
                    testId="toggle--general"
                >
                    {
                        agendaTopics.map((agendaTopic) => {
                            const isIncluded = this.isIncluded(agendaTopic._id);

                            return (
                                <CheckboxInput
                                    key={agendaTopic._id}
                                    value={isIncluded}
                                    onChange={() => {
                                        this.handleChange(isIncluded, agendaTopic);
                                    }}
                                    label={gettext(agendaTopic.label)}
                                />
                            );
                        })
                    }
                </FormToggle>
            </div>
        ) : (
            <div className="empty-state__container mt-3">
                <div className="empty-state">
                    <figure className="empty-state__graphic">
                        <img src="/static/empty-states/empty_state--small.svg" role="presentation" alt="" />
                    </figure>
                    <figcaption className="empty-state__text">
                        <h4 className="empty-state__text-heading">You don't have any saved Topics yet</h4>
                        <p className="empty-state__text-description">
                            You can create Topics by saving search terms and/or filters from the Wire and Agenda sections.
                        </p>
                        <div className="empty-state__links">
                            <a className="" href="">Go to Wire</a>
                            <a className="" href="">Go to Agenda</a>
                        </div>
                    </figcaption>
                </div>
            </div>
        );

        return (
            <Modal
                width="full"
                closeModal={this.props.closeModal}
                title={gettext('Personalize Home')}
                onSubmitLabel={gettext('Save')}
                disableButtonOnSubmit
            >
                <div
                    style={{
                        display: 'flex',
                        flexDirection: 'row',
                    }}
                >
                    <aside className="full-page-layout__content-aside">
                        <div className="full-page-layout__content-aside-inner">
                            <p className='font-size--medium text-color--muted mt-1 mb-3'>Select up to 6 Topics you want to display on your personal Home screen.</p>
                            <p className='font-size--large'>{this.state.checkedTopics.length} out of 6 topics selected</p>
                            <RadioButtonGroup
                                activeOptionId={this.state.activeSection}
                                options={[
                                    {
                                        _id: '1',
                                        name: 'My topics'
                                    },
                                    {
                                        _id: '2',
                                        name: 'Company topics'
                                    },
                                ]}
                                switchOptions={(optionId) => {
                                    this.setState({
                                        activeSection: optionId
                                    });
                                }}
                            />
                            <div style={{padding: 6}} />
                            <div
                                className="search search--small search--with-icon search--bordered m-0"
                            >
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
                                        placeholder="Search Topics"
                                        aria-label="Search Topics"
                                    />
                                    <div className="search__form-buttons">
                                        <button className="search__button-clear" aria-label="Clear search" type="reset">
                                            <svg fill="none" height="18" viewBox="0 0 18 18" width="18" xmlns="http://www.w3.org/2000/svg">
                                                <path clipRule="evenodd" d="m9 18c4.9706 0 9-4.0294 9-9 0-4.97056-4.0294-9-9-9-4.97056 0-9 4.02944-9 9 0 4.9706 4.02944 9 9 9zm4.9884-12.58679-3.571 3.57514 3.5826 3.58675-1.4126 1.4143-3.58252-3.5868-3.59233 3.5965-1.41255-1.4142 3.59234-3.59655-3.54174-3.54592 1.41254-1.41422 3.54174 3.54593 3.57092-3.57515z" fill="var(--color-text)" fillRule="evenodd" opacity="1"></path>
                                            </svg>
                                        </button>
                                    </div>
                                </form>
                            </div>
                            {this.state.searchTerm ? searchedTopics : groupedTopics}
                        </div>
                    </aside>
                    <div
                        style={{
                            width: '75%',
                            display: 'flex',
                            flexDirection: 'column',
                        }}
                    >
                        <Input disabled value={gettext('My Home')} />
                        {/* <CheckboxInput
                            value={this.state.checked}
                            onChange={() => {
                                this.setState({
                                    checked: !this.state.checked,
                                });
                            }}
                            label={gettext('Make this my default home screen')}
                        /> */}
                        <div className="py-3 mt-4 mb-2 border border--medium border-start-0 border-end-0 border--dotted">
                            <p className='font-size--medium text-color--muted m-0'>
                                <span className='text-color--default fw-bold'>Hint: </span>
                                Drag and drop items to change the order. This will change the order of the topics are displayed on the Home screen.
                            </p>
                        </div>
                        <div className="simple-card__list pt-3">
                            {
                                this.state.checkedTopics.map((topic) => (
                                    <div
                                        key={topic._id}
                                        className="simple-card flex-row simple-card--compact simple-card--draggable"
                                    >
                                        <div style={{paddingLeft: 24}} className='simple-card__content'>
                                            <h6 className="simple-card__headline" title="">{topic.label}</h6>
                                            <div className="simple-card__row">
                                                <div className="simple-card__column simple-card__column--align-start">
                                                    <span className="simple-card__date">
                                                        {topic.company != null ? 'Company Topics' : 'My Topics'}
                                                    </span>
                                                </div>
                                            </div>
                                        </div>
                                        <div className='simple-card__actions'>
                                            <button type="button" className="icon-button icon-button--secondary icon-button--small" title="" aria-label="Delete"><i className="icon--trash"></i></button>
                                        </div>
                                    </div>
                                ))
                            }
                        </div>
                    </div>
                </div>
            </Modal>
        );
    }
}

const mapStateToProps = (state: IReduxStoreProps) => ({
    formValid: get(state, 'modal.formValid'),
    topics: state.topics,
});

const mapDispatchToProps = (dispatch: any) => ({
    reloadTopics: () => dispatch(reloadMyWireTopics(true))
});

export const PersonalizeHomeSettingsModal: React.ComponentType<any> =
    connect(mapStateToProps, mapDispatchToProps)(PersonalizeHomeModal);
