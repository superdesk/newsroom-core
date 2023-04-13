import * as React from 'react';
import PropTypes from 'prop-types';
import Toggle from 'react-toggle';

import {gettext} from 'utils';

export class ListSearchOptions extends React.PureComponent<any, any> {
    constructor(props: any) {
        super(props);

        this.state = {isOpen: false};
        this.btnGroup = null;
    }

    componentDidMount() {
        if (this.btnGroup) {
            this.btnGroup.addEventListener('shown.bs.dropdown', () => {
                this.setState({isOpen: true});
            });
            this.btnGroup.addEventListener('hidden.bs.dropdown', () => {
                this.setState({isOpen: false});
            });
        }
    }

    render() {
        return (
            <div
                className="btn-group"
                ref={(elem) => this.btnGroup = elem}
            >
                <button
                    id="listSearchOptionsButton"
                    className="content-bar__menu"
                    onClick={this.toggleOpen}
                    data-bs-toggle="dropdown"
                    aria-haspopup="menu"
                    aria-expanded={this.state.isOpen}
                    aria-label={gettext('Search Options')}
                    role="button"
                >
                    <i className="icon--settings" />
                </button>
                <div
                    className='dropdown-menu dropdown-menu-right'
                    aria-labelledby="listSearchOptionsButton"
                >
                    <h6 className='dropdown-header'>{gettext('Search Options')}</h6>
                    <form className="px-3 pt-3">
                        {this.props.hideSearchAllVersions ? null : (
                            <div className="form-group d-flex align-items-center">
                                <Toggle
                                    id="all-versions"
                                    checked={this.props.searchAllVersions}
                                    className="toggle-background"
                                    icons={false}
                                    onChange={this.props.toggleSearchAllVersions}
                                />
                                <label
                                    htmlFor="all-versions"
                                    className="mb-0 ms-2"
                                >
                                    {gettext('All Versions')}
                                </label>
                            </div>
                        )}

                        {this.props.hideNewsOnly ? null : (
                            <div className="form-group d-flex align-items-center">
                                <Toggle
                                    id="news-only"
                                    checked={this.props.newsOnly}
                                    className="toggle-background"
                                    icons={false}
                                    onChange={this.props.toggleNews}
                                />
                                <label
                                    htmlFor="news-only"
                                    className="mb-0 ms-2"
                                >
                                    {gettext('News Only')}
                                </label>
                            </div>
                        )}
                    </form>
                </div>
            </div>
        );
    }
}

ListSearchOptions.propTypes = {
    newsOnly: PropTypes.bool,
    toggleNews: PropTypes.func,
    hideNewsOnly: PropTypes.bool,
    hideSearchAllVersions: PropTypes.bool,
    searchAllVersions: PropTypes.bool,
    toggleSearchAllVersions: PropTypes.func,
};
