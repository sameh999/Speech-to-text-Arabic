
import push_file_to_github as pushto
repo_slug = "sameh999/Speech-to-text-Arabic"
branch = "main"
user ="sameh999"
token = "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"
fileName = "results.txt"
gitHubFileName = "results.txt"

pushto.push_to_repo_branch(gitHubFileName, fileName, repo_slug, branch, user, token)
